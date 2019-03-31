'''aws cromwell runner'''

import os
import json
import tempfile
import logging
import yaml
import utils.pipeline

def filter_list(alist, blist):
    '''remove blist from alist'''
    return list(set(alist)-set(blist))

def get_cwl_steps(cwlwf):
    '''get cwl steps names'''
    cwl = dict()
    with open(cwlwf, 'r') as fhandle:
        cwl = yaml.load(fhandle)
    cwl_steps = cwl['steps'].keys()
    return cwl_steps

def dict_to_string(list_of_dict):
    '''convert list of dict to list of strings'''
    list_of_string = []
    if list_of_dict:
        for i in list_of_dict:
            list_of_string.append(str(i))
    else:
        return None
    return list_of_string

def freebayes(args):
    '''run freebayes cohort genotyping'''
    freebayes_template_json = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        "etc/aws_freebayes.json"
    )
    input_data = utils.pipeline.load_json(freebayes_template_json)
    input_data['job_uuid'] = args.job_uuid
    input_data['bam_files'] = utils.pipeline.create_cwl_array_input(args.bam_files_manifest)
    input_data['freebayes_thread_count'] = args.freebayes_thread_count
    input_data['number_of_chunks_for_freebayes'] = args.number_of_chunks_for_freebayes
    input_data['upload_s3_bucket'] = os.path.join(
        args.upload_s3_bucket,
        args.project,
        args.batch_id,
        args.job_uuid
    )
    workflow_meta = {
        'basedir': args.basedir,
        'project': args.project,
        'batch_id': args.batch_id,
        'job_uuid': args.job_uuid,
        'cromwell_config': os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                )
            ),
            "cromwell/cromwell.aws.conf"
        ),
        'cromwell_jar_path': args.cromwell_jar_path,
        'cwlwf': os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                )
            ),
            "aws_genomel_cohort_freebayes.cwl"
        ),
        'cwl_pack': os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                )
            ),
            "cwl.zip"
        )
    }
    freebayes = CromwellRunner(
        workflow_meta=workflow_meta,
        input_data=input_data
    )
    freebayes.run()

class CromwellRunner(object):
    '''this class describes GenoMEL-AWS freebayes cromwell runner'''
    def __init__(self, workflow_meta, input_data):
        '''
        workflow_meta.keys() = [
            'basedir',
            'project',
            'batch_id',
            'job_uuid',
            'cromwell_config',
            'cromwell_jar_path',
            'cwlwf',
            'cwl_pack'
        ]
        '''
        self.input_data = input_data
        # setup workflow metadata
        self.workflow_meta = workflow_meta
        self.log_data = utils.pipeline.cohort_data_template()
        self.workflow_meta['base_s3_loc'] = self.input_data['upload_s3_bucket']
        self.workflow_meta['log_file'] = None
        self.workflow_meta['cwl_input_json'] = self._cwl_input_json()
        self.workflow_meta['cromwell_metadata_output'] = self._cromwell_metadata_output()
        self.workflow_meta['log_dir'] = None
        self.workflow_meta['cwl_log_tar'] = None
        self.workflow_meta['cromwell_start'] = None
        self.workflow_meta['cromwell_end'] = None
        self.workflow_meta['cromwell_status'] = None
        self.workflow_meta['cromwell_failures'] = None
        self.workflow_meta['cromwell_cwl_outputs'] = None
        self.workflow_meta['cromwell_cwl_logs'] = None
        self.workflow_meta['cromwell_finished_steps'] = None
        self.workflow_meta['cromwell_todo_steps'] = None
        self.workflow_meta['runner_failure'] = None
        self.workflow_meta['output_vcf'] = list()
        self.workflow_meta['output_vcf_url'] = list()
        self.workflow_meta['output_vcf_local'] = list()
        self.workflow_meta['output_vcf_md5sum'] = list()
        self.workflow_meta['output_vcf_filesize'] = list()
        self.workflow_meta['pipeline_time'] = 0.0
        self.workflow_meta['pipeline_avg_cpu_percentage'] = 0
        self.cwl_steps = get_cwl_steps(self.workflow_meta['cwlwf'])

    def run(self):
        '''main pipeline'''
        # setup work env
        os.chdir(self.workflow_meta['basedir'])
        logger = self._log()
        # make sure cwltool in the path
        # os.environ['PATH'] = "/home/ubuntu/.virtualenvs/p2/bin/:$PATH"
        # cromwell cmd
        cmd = [
            '/usr/bin/java',
            '-Dconfig.file={}'.format(self.workflow_meta['cromwell_config']),
            '-jar', self.workflow_meta['cromwell_jar_path'],
            'run', self.workflow_meta['cwlwf'],
            '-i', self.workflow_meta['cwl_input_json'],
            '--imports', self.workflow_meta['cwl_pack'],
            '--metadata-output', self.workflow_meta['cromwell_metadata_output']
        ]
        logger.info('%s', cmd)
        try:
            # run cromwell
            utils.pipeline.run_command(cmd, logger)
            # cromwell status
            self._extract_cromwell_output_metadata()
            if not self.workflow_meta['cromwell_failures'] \
                and not self.workflow_meta['runner_failure']:
                # calculate cpu percentage
                self._calculate_cwl_metadata()
                tar_exit = self._tar_log(logger)
                if tar_exit:
                    self.workflow_meta['runner_failure'] = 'tar_logs_fails'
                # upload log files
                upload_exit = self._upload_log_files(logger)
                if upload_exit:
                    self.workflow_meta['runner_failure'] = 'upload_logs_fails'
                else:
                    self._process_job_success()
        except BaseException, error:
            logger.error('Failed: %s', error)
            self.workflow_meta['runner_failure'] = '{}'.format(error)
        if self.workflow_meta['cromwell_failures'] or self.workflow_meta['runner_failure']:
            self._process_job_fail()
        logger.info('%s', self.log_data)
        
    def create_tmp_dir(self, prefix):
        '''create cwl tmp directory'''
        tmpdir = tempfile.mkdtemp(prefix="{}".format(prefix), dir=self.workflow_meta['basedir'])
        return tmpdir

    def _cwl_input_json(self):
        '''prepare cwl input json'''
        cwl_input_json = os.path.join(
            self.workflow_meta['basedir'], 'aws_genomel_freebayes.{0}.{1}.{2}.json'.format(
                self.workflow_meta['project'],
                self.workflow_meta['batch_id'],
                self.workflow_meta['job_uuid']
            )
        )
        with open(cwl_input_json, 'wt') as ohandle:
            json.dump(self.input_data, ohandle, indent=4)
        return cwl_input_json

    def _cromwell_metadata_output(self):
        '''prepare cromwell metadata output'''
        output_json = os.path.join(
            self.workflow_meta['basedir'], 'aws_genomel_freebayes.{0}.{1}.{2}.output'.format(
                self.workflow_meta['project'],
                self.workflow_meta['batch_id'],
                self.workflow_meta['job_uuid']
            )
        )
        return output_json

    def _log(self):
        '''setup log file'''
        log_file = os.path.join(
            self.workflow_meta['basedir'], 'aws_genomel_freebayes.{0}.{1}.{2}.log'.format(
                self.workflow_meta['project'],
                self.workflow_meta['batch_id'],
                self.workflow_meta['job_uuid']
            )
        )
        self.workflow_meta['log_file'] = log_file
        logger = utils.pipeline.setup_logging(
            logging.INFO,
            self.workflow_meta['job_uuid'],
            log_file
        )
        return logger

    def _extract_cromwell_output_metadata(self):
        '''extract metadata from cromwell output'''
        if not os.path.isfile(self._cromwell_metadata_output()):
            self.workflow_meta['runner_failure'] = 'no_cromwell_metadata_output'
        else:
            metadata_json = utils.pipeline.load_json(self._cromwell_metadata_output())
            self.workflow_meta['cromwell_failures'] = dict_to_string(
                metadata_json.get('failures')
            )
            self.workflow_meta['cromwell_start'] = metadata_json['start']
            self.workflow_meta['cromwell_end'] = metadata_json['end']
            self.workflow_meta['cromwell_status'] = metadata_json['status']
            self.workflow_meta['cromwell_cwl_outputs'] = metadata_json['outputs']
            self.workflow_meta['cromwell_finished_steps'] = metadata_json['calls'].keys()
            self.workflow_meta['cromwell_todo_steps'] = filter_list(
                self.cwl_steps, self.workflow_meta['cromwell_finished_steps']
            )

    def _calculate_cwl_metadata(self):
        '''gather and calculate cwl metadata'''
        self.workflow_meta['cromwell_cwl_logs'] = []
        for key, value in self.workflow_meta['cromwell_cwl_outputs'].items():
            if key.endswith('time_logs'):
                for log in value:
                    self.workflow_meta['cromwell_cwl_logs'].append(log['location'])
        pipeline_cpu_usage = []
        pipeline_cpu_time = []
        for log in self.workflow_meta['cromwell_cwl_logs']:
            dic = utils.pipeline.load_json(log)
            cpu_percent = float(dic['percent_of_cpu'][:-1])
            step_weight = float(dic['wall_clock'])
            pipeline_cpu_usage.append(cpu_percent * step_weight)
            pipeline_cpu_time.append(step_weight)
        pipeline_time = sum(pipeline_cpu_time)
        pipeline_avg_cpu_usage = str(int(sum(pipeline_cpu_usage)/sum(pipeline_cpu_time))) + '%'
        self.workflow_meta['pipeline_time'] = pipeline_time
        self.workflow_meta['pipeline_avg_cpu_percentage'] = pipeline_avg_cpu_usage

    def _tar_log(self, logger):
        '''make tar for all cwl time logs'''
        self.workflow_meta['log_dir'] = self.create_tmp_dir('cwl_logs_')
        for log in self.workflow_meta['cromwell_cwl_logs']:
            utils.pipeline.move_file(log, self.workflow_meta['log_dir'])
        self.workflow_meta['cwl_log_tar'] = os.path.join(
            self.workflow_meta['basedir'], \
            'aws_genomel_freebayes.{0}.{1}.{2}.cwl_logs.tar.bz2'.format(
                self.workflow_meta['project'],
                self.workflow_meta['batch_id'],
                self.workflow_meta['job_uuid']
            )
        )
        exit_code = utils.pipeline.targz_compress(
            logger,
            self.workflow_meta['cwl_log_tar'],
            self.workflow_meta['log_dir']
        )
        return exit_code

    def _upload_log_files(self, logger):
        '''upload tar file of all cwl logs'''
        to_upload_dir = self.create_tmp_dir('to_upload_')
        utils.pipeline.move_file(self.workflow_meta['cwl_input_json'], to_upload_dir)
        utils.pipeline.move_file(self.workflow_meta['cwl_log_tar'], to_upload_dir)
        exit_code = utils.pipeline.aws_s3_put(
            logger=logger,
            remote_output=self.workflow_meta['base_s3_loc'],
            local_input=to_upload_dir,
            profile=self.input_data['upload_s3_profile'],
            endpoint_url=self.input_data['upload_s3_endpoint'],
            recursive=True
        )
        return exit_code

    def _get_output_meta(self):
        '''get output vcf'''
        for key, value in self.workflow_meta['cromwell_cwl_outputs'].items():
            if key.endswith('vcf'):
                self.workflow_meta['output_vcf_local'].append(value['location'])
                self.workflow_meta['output_vcf_filesize'].append(value['size'])
                self.workflow_meta['output_vcf'].append(
                    os.path.basename(value['location'])
                )
                self.workflow_meta['output_vcf_md5sum'].append(
                    utils.pipeline.get_md5(value['location'])
                )
                self.workflow_meta['output_vcf_url'].append(
                    os.path.join(
                        self.workflow_meta['base_s3_loc'],
                        os.path.basename(value['location'])
                    )
                )

    def _process_job_success(self):
        '''process when job successes'''
        self.log_data['job_uuid'] = self.workflow_meta['job_uuid']
        self.log_data['batch_id'] = self.workflow_meta['batch_id']
        self.log_data['project'] = self.workflow_meta['project']
        self.log_data['cromwell_status'] = self.workflow_meta['cromwell_status']
        self.log_data['cromwell_failures'] = self.workflow_meta['cromwell_failures']
        self.log_data['cromwell_finished_steps'] = self.workflow_meta['cromwell_finished_steps']
        self.log_data['cromwell_todo_steps'] = self.workflow_meta['cromwell_todo_steps']
        self.log_data['datetime_start'] = self.workflow_meta['cromwell_start']
        self.log_data['datetime_end'] = self.workflow_meta['cromwell_end']
        self._get_output_meta()
        self.log_data['vcf_url'] = self.workflow_meta['output_vcf_url']
        self.log_data['vcf_local_path'] = self.workflow_meta['output_vcf_local']
        self.log_data['vcf_md5sum'] = self.workflow_meta['output_vcf_md5sum']
        self.log_data['vcf_filesize'] = self.workflow_meta['output_vcf_filesize']
        self.log_data['cwl_walltime'] = self.workflow_meta['pipeline_time']
        self.log_data['cwl_cpu_percentage'] = self.workflow_meta['pipeline_avg_cpu_percentage']
        self.log_data['cwl_input_json'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            os.path.basename(self.workflow_meta['cwl_input_json'])
        )
        self.log_data['time_metrics_json'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            os.path.basename(self.workflow_meta['cwl_log_tar'])
        )
        self.log_data['cromwell_version'] = os.path.basename(
            self.workflow_meta['cromwell_jar_path']
        )
        self.log_data['debug_path'] = self.workflow_meta['log_file']

    def _process_job_fail(self):
        '''process when job fails'''
        self.log_data['job_uuid'] = self.workflow_meta['job_uuid']
        self.log_data['batch_id'] = self.workflow_meta['batch_id']
        self.log_data['project'] = self.workflow_meta['project']
        self.log_data['runner_failures'] = self.workflow_meta['runner_failure']
        self.log_data['cromwell_status'] = self.workflow_meta['cromwell_status']
        self.log_data['cromwell_failures'] = self.workflow_meta['cromwell_failures']
        self.log_data['cromwell_finished_steps'] = self.workflow_meta['cromwell_finished_steps']
        self.log_data['cromwell_todo_steps'] = self.workflow_meta['cromwell_todo_steps']
        self.log_data['datetime_start'] = self.workflow_meta['cromwell_start']
        self.log_data['datetime_end'] = self.workflow_meta['cromwell_end']
        self.log_data['cromwell_version'] = os.path.basename(
            self.workflow_meta['cromwell_jar_path']
        )
        self.log_data['debug_path'] = self.workflow_meta['log_file']    
