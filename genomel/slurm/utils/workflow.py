'''pipeline runner'''

import os
import json
import time
import glob
import logging
import tempfile
import datetime
import utils.pipeline
import postgres.metrics
import postgres.utils

def run_alignment(args):
    '''run alignment'''
    input_data = utils.pipeline.load_template_json()['alignment_template']
    sample_list = [args.aliquot_id] * len(args.readgroup_names)
    pu_list = [args.job_uuid] * len(args.readgroup_names)
    rgl_list = ['@RG\tCN:CGR\tPL:ILLUMINA\tID:{RG}\tSM:{SM}\tPU:{PU}\tLB:Library'\
        .format(RG=rg, SM=sm, PU=pu) \
        for rg, sm, pu in zip(args.readgroup_names, sample_list, pu_list)]
    input_data['job_uuid'] = args.job_uuid
    input_data['fastq_read1_uri'] = args.fastq_read1_uri
    input_data['fastq_read2_uri'] = args.fastq_read2_uri
    input_data['fastq_read1_md5'] = args.fastq_read1_md5
    input_data['fastq_read2_md5'] = args.fastq_read2_md5
    input_data['readgroup_lines'] = rgl_list
    input_data['readgroup_names'] = args.readgroup_names
    workflow_meta = {
        'basedir': args.basedir,
        'pipeline': args.choice,
        'project': args.project,
        'job_uuid': args.job_uuid,
        'aliquot_id': args.aliquot_id,
        'input_table': args.input_table,
        'cwlwf': args.cwlwf
    }
    genomel = GenomelIndiv(
        workflow_meta=workflow_meta,
        input_data=input_data,
        psql_conf=args.psql_conf)
    genomel.run()

def run_harmonization(args):
    '''run harmonization'''
    input_data = utils.pipeline.load_template_json()['harmonization_template']
    input_data['job_uuid'] = args.job_uuid
    input_data['bam_uri'] = args.bam_uri
    input_data['bam_md5'] = args.bam_md5
    workflow_meta = {
        'basedir': args.basedir,
        'pipeline': args.choice,
        'project': args.project,
        'job_uuid': args.job_uuid,
        'aliquot_id': args.aliquot_id,
        'input_table': args.input_table,
        'cwlwf': args.cwlwf
    }
    genomel = GenomelIndiv(
        workflow_meta=workflow_meta,
        input_data=input_data,
        psql_conf=args.psql_conf)
    genomel.run()

class GenomelIndiv(object):
    '''this class describes GenoMEL-Bionimbus Protected Data Cloud pipelines'''
    def __init__(self, workflow_meta, input_data, psql_conf):
        '''
        workflow_meta.keys() = [
            'basedir',
            'pipeline',
            'project',
            'job_uuid',
            'aliquot_id',
            'input_table',
            'cwlwf'
        ]
        '''
        self.input_data = input_data
        self.pg_data = utils.pipeline.pg_data_template()
        self.psql_conf = psql_conf
        self.psql_class = postgres.metrics.GenomelIndividualMetrics
        # setup workflow metadata
        self.workflow_meta = workflow_meta
        self.workflow_meta['base_s3_loc'] = os.path.join(
            self.input_data['upload_s3_bucket'],
            self.workflow_meta['job_uuid']
        )
        self.workflow_meta['log_file'] = None
        self.workflow_meta['cwl_input_json'] = self._cwl_input_json()
        self.workflow_meta['cwl_output_json'] = self._cwl_output_json()
        self.workflow_meta['log_dir'] = None
        self.workflow_meta['cwl_log_tar'] = None
        self.workflow_meta['cwl_start'] = None
        self.workflow_meta['cwl_end'] = None
        self.workflow_meta['cwl_failure'] = False
        self.workflow_meta['runner_failure'] = False
        self.workflow_meta['pipeline_time'] = 0.0
        self.workflow_meta['pipeline_avg_cpu_percentage'] = 0
        self.workflow_meta['haplotypecaller_time'] = 0.0
        self.workflow_meta['haplotypecaller_avg_cpu_percentage'] = 0

    def run(self):
        '''main pipeline'''
        # setup start-time
        self.workflow_meta['cwl_start'] = time.time()
        self.workflow_meta['datetime_start'] = str(datetime.datetime.now())
        # setup work env
        os.chdir(self.workflow_meta['basedir'])
        tmpdir = self.create_tmp_dir('tmpdir_')
        logger = self._log()
        # cwl cmd
        cmd = [
            '/home/ubuntu/.virtualenvs/p2/bin/cwltool',
            '--debug',
            '--relax-path-checks',
            '--outdir', self.workflow_meta['basedir'],
            '--tmpdir-prefix', tmpdir,
            '--tmp-outdir-prefix', tmpdir,
            self.workflow_meta['cwlwf'],
            self.workflow_meta['cwl_input_json']
        ]
        # run cwl
        cwl_exit = utils.pipeline.run_command(cmd, logger, self.workflow_meta['cwl_output_json'])
        # cwl status
        if cwl_exit:
            self.workflow_meta['cwl_failure'] = True
        # calculate cpu percentage
        self._calculate_cpu_percentage()
        # tar all logs
        tar_exit = self._tar_log(logger)
        if tar_exit:
            self.workflow_meta['runner_failure'] = True
        # upload ancillary files
        upload_exit = self._upload_ancillary_files(logger)
        if upload_exit:
            self.workflow_meta['runner_failure'] = True
        # update psql
        if not self.workflow_meta['cwl_failure'] and not self.workflow_meta['runner_failure']:
            self._process_cwl_success()
        else:
            self._process_cwl_fail()
        engine = postgres.utils.get_db_engine(self.psql_conf)
        postgres.metrics.add_metrics(engine, self.psql_class, self.pg_data)
        # clean up
        utils.pipeline.remove_dir(self.workflow_meta['basedir'])

    def _cwl_input_json(self):
        '''prepare cwl input json'''
        cwl_input_json = os.path.join(
            self.workflow_meta['basedir'], 'genomel_individual.{0}.{1}.{2}.{3}.json'.format(
                self.workflow_meta['pipeline'],
                self.workflow_meta['project'],
                self.workflow_meta['job_uuid'],
                self.workflow_meta['aliquot_id']
            )
        )
        with open(cwl_input_json, 'wt') as ohandle:
            json.dump(self.input_data, ohandle, indent=4)
        return cwl_input_json

    def _cwl_output_json(self):
        '''prepare cwl output json'''
        cwl_output_json = os.path.join(
            self.workflow_meta['basedir'], 'genomel_individual.{0}.{1}.{2}.{3}.output'.format(
                self.workflow_meta['pipeline'],
                self.workflow_meta['project'],
                self.workflow_meta['job_uuid'],
                self.workflow_meta['aliquot_id']
            )
        )
        return cwl_output_json

    def create_tmp_dir(self, prefix):
        '''create cwl tmp directory'''
        tmpdir = tempfile.mkdtemp(prefix="{}".format(prefix), dir=self.workflow_meta['basedir'])
        return tmpdir

    def _log(self):
        '''setup log file'''
        log_file = os.path.join(
            os.path.dirname(self.workflow_meta['basedir']),
            'genomel_individual.{0}.{1}.{2}.{3}.log'.format(
                self.workflow_meta['pipeline'],
                self.workflow_meta['project'],
                self.workflow_meta['job_uuid'],
                self.workflow_meta['aliquot_id']
            )
        )
        self.workflow_meta['log_file'] = log_file
        logger = utils.pipeline.setup_logging(
            logging.INFO,
            self.workflow_meta['job_uuid'],
            log_file
        )
        return logger

    def _calculate_cpu_percentage(self):
        '''calculate average cpu percentage'''
        cwl_logs = glob.glob(
            '{}/{}*time.json'.format(
                self.workflow_meta['basedir'],
                self.workflow_meta['job_uuid']
            )
        )
        pipeline_cpu_usage = []
        pipeline_cpu_time = []
        haplotypecaller_cpu_usage = []
        haplotypecaller_cpu_time = []
        if cwl_logs:
            for log in cwl_logs:
                dic = utils.pipeline.load_json(log)
                cpu_percent = float(dic['percent_of_cpu'][:-1])
                step_weight = float(dic['wall_clock'])
                if 'gatk3' in log or 'picard' in log:
                    haplotypecaller_cpu_usage.append(cpu_percent * step_weight)
                    haplotypecaller_cpu_time.append(step_weight)
                else:
                    pipeline_cpu_usage.append(cpu_percent * step_weight)
                    pipeline_cpu_time.append(step_weight)
            pipeline_time = sum(pipeline_cpu_time)
            pipeline_avg_cpu_usage = str(int(sum(pipeline_cpu_usage)/sum(pipeline_cpu_time))) + '%'
            haplotypecaller_time = sum(haplotypecaller_cpu_time)
            haplotypecaller_avg_cpu_usage = str(
                int(sum(haplotypecaller_cpu_usage)/sum(haplotypecaller_cpu_time))
            ) + '%'
        else:
            pipeline_time = None
            pipeline_avg_cpu_usage = None
            haplotypecaller_time = None
            haplotypecaller_avg_cpu_usage = None
        self.workflow_meta['pipeline_time'] = pipeline_time
        self.workflow_meta['pipeline_avg_cpu_percentage'] = pipeline_avg_cpu_usage
        self.workflow_meta['haplotypecaller_time'] = haplotypecaller_time
        self.workflow_meta['haplotypecaller_avg_cpu_percentage'] = haplotypecaller_avg_cpu_usage

    def _tar_log(self, logger):
        '''make tar for all cwl time logs'''
        cwl_logs = glob.glob('{}/*time.json'.format(self.workflow_meta['basedir']))
        if cwl_logs:
            self.workflow_meta['log_dir'] = self.create_tmp_dir('cwl_logs_')
            for log in cwl_logs:
                utils.pipeline.move_file(log, self.workflow_meta['log_dir'])
            self.workflow_meta['cwl_log_tar'] = os.path.join(
                self.workflow_meta['basedir'], \
                'genomel_individual.{0}.{1}.{2}.{3}.cwl_logs.tar.bz2'.format(
                    self.workflow_meta['pipeline'],
                    self.workflow_meta['project'],
                    self.workflow_meta['job_uuid'],
                    self.workflow_meta['aliquot_id']
                )
            )
            exit_code = utils.pipeline.targz_compress(
                logger,
                self.workflow_meta['cwl_log_tar'],
                self.workflow_meta['log_dir']
            )
        else: exit_code = 1
        return exit_code

    def _upload_ancillary_files(self, logger):
        '''upload tar file of all cwl logs'''
        to_upload_dir = self.create_tmp_dir('to_upload_')
        utils.pipeline.move_file(self.workflow_meta['cwl_input_json'], to_upload_dir)
        if self.workflow_meta['cwl_log_tar']:
            utils.pipeline.move_file(self.workflow_meta['cwl_log_tar'], to_upload_dir)
        remote_loc = os.path.join(
            self.input_data['upload_s3_bucket'],
            self.workflow_meta['job_uuid']
        )
        exit_code = utils.pipeline.aws_s3_put(
            logger=logger,
            remote_output=remote_loc,
            local_input=to_upload_dir,
            profile=self.input_data['upload_s3_profile'],
            endpoint_url=self.input_data['upload_s3_endpoint'],
            recursive=True
        )
        return exit_code

    def _time(self, handle):
        '''extract time from cwl logs'''
        logs = glob.glob('{}/{}'.format(format(self.workflow_meta['log_dir']), handle))
        time_list = []
        if logs:
            for log in logs:
                dic = utils.pipeline.load_json(log)
                _time = float(dic['wall_clock'])
                time_list.append(_time)
            total_time = sum(time_list)
        else: total_time = None
        return total_time

    def _stage_local(self, indiv):
        '''stage cwl output to local gluster'''
        indiv_dir = os.path.join(
            '/mnt/glusterfs',
            'genomel_individual.{0}.{1}.{2}.{3}'.format(
                self.workflow_meta['pipeline'],
                self.workflow_meta['project'],
                self.workflow_meta['job_uuid'],
                self.workflow_meta['aliquot_id']
            )
        )
        if not os.path.isdir(indiv_dir):
            os.mkdir(indiv_dir)
        utils.pipeline.move_file(indiv, indiv_dir)
        return os.path.join(indiv_dir, os.path.basename(indiv))

    def _process_cwl_success(self):
        '''process when cwl successes'''
        download_time = self._time('aws_download*')
        bam_upload_time = self._time('aws_upload*duplicates_marked.sorted*')
        gvcf_upload_time = self._time('aws_upload*haplotypecaller*')
        cwl_output = utils.pipeline.load_json(self.workflow_meta['cwl_output_json'])
        bam_local_path = self._stage_local(
            cwl_output['genomel_bam']['path']
        )
        self._stage_local(cwl_output['genomel_bam']['secondaryFiles'][0]['path'])
        gvcf_local_path = self._stage_local(
            cwl_output['genomel_gvcf']['path']
        )
        self._stage_local(cwl_output['genomel_gvcf']['secondaryFiles'][0]['path'])
        self.workflow_meta['cwl_end'] = time.time()
        self.pg_data['job_uuid'] = self.workflow_meta['job_uuid']
        self.pg_data['aliquot_id'] = self.workflow_meta['aliquot_id']
        self.pg_data['input_table'] = self.workflow_meta['input_table']
        self.pg_data['project'] = self.workflow_meta['project']
        self.pg_data['status'] = "COMPLETED"
        self.pg_data['datetime_start'] = self.workflow_meta['datetime_start']
        self.pg_data['datetime_end'] = str(datetime.datetime.now())
        self.pg_data['download_time'] = download_time
        self.pg_data['bam_upload_time'] = bam_upload_time
        self.pg_data['gvcf_upload_time'] = gvcf_upload_time
        self.pg_data['bam_url'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            cwl_output['genomel_bam']['basename']
        )
        self.pg_data['gvcf_url'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            cwl_output['genomel_gvcf']['basename']
        )
        self.pg_data['bam_local_path'] = bam_local_path
        self.pg_data['gvcf_local_path'] = gvcf_local_path
        self.pg_data['bam_md5sum'] = utils.pipeline.get_md5(bam_local_path)
        self.pg_data['gvcf_md5sum'] = utils.pipeline.get_md5(gvcf_local_path)
        self.pg_data['bam_filesize'] = utils.pipeline.get_file_size(bam_local_path)
        self.pg_data['gvcf_filesize'] = utils.pipeline.get_file_size(gvcf_local_path)
        if self.workflow_meta['pipeline'] == 'alignment':
            self.pg_data['alignment_cwl_walltime'] = self.workflow_meta['pipeline_time']
            self.pg_data['alignment_cwl_cpu_percentage'] = self.workflow_meta\
                ['pipeline_avg_cpu_percentage']
        else:
            self.pg_data['harmonization_cwl_walltime'] = self.workflow_meta['pipeline_time']
            self.pg_data['harmonization_cwl_cpu_percentage'] = self.workflow_meta\
                ['pipeline_avg_cpu_percentage']
        self.pg_data['haplotypecaller_cwl_walltime'] = self.workflow_meta['haplotypecaller_time']
        self.pg_data['haplotypecaller_cwl_cpu_percentage'] = self.workflow_meta\
            ['haplotypecaller_avg_cpu_percentage']
        self.pg_data['whole_workflow_elapsed'] = float(
            self.workflow_meta['cwl_end'] - self.workflow_meta['cwl_start']
        )
        self.pg_data['cwl_input_json'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            os.path.basename(self.workflow_meta['cwl_input_json'])
        )
        self.pg_data['time_metrics_json'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            os.path.basename(self.workflow_meta['cwl_log_tar'])
        )
        self.pg_data['debug_path'] = self.workflow_meta['log_file']

    def _process_cwl_fail(self):
        '''process when cwl fails'''
        if self.workflow_meta['cwl_failure']:
            cwl_output = utils.pipeline.load_json(self.workflow_meta['cwl_output_json'])
            if cwl_output:
                if cwl_output['genomel_gvcf']:
                    status = "FAILED_WHEN_UPLOAD"
                elif cwl_output['genomel_bam']:
                    status = "FAILED_IN_VARIANT_CALLING"
                else:
                    status = "FAILED_IN_EARLY_STAGE"
            else: status = "FAILED_IN_CWL"
        else: status = "FAILED_IN_PYTHON_RUNNER"
        self.workflow_meta['cwl_end'] = time.time()
        self.pg_data['job_uuid'] = self.workflow_meta['job_uuid']
        self.pg_data['aliquot_id'] = self.workflow_meta['aliquot_id']
        self.pg_data['input_table'] = self.workflow_meta['input_table']
        self.pg_data['project'] = self.workflow_meta['project']
        self.pg_data['status'] = status
        self.pg_data['datetime_start'] = self.workflow_meta['datetime_start']
        self.pg_data['datetime_end'] = str(datetime.datetime.now())
        self.pg_data['whole_workflow_elapsed'] = float(
            self.workflow_meta['cwl_end'] - self.workflow_meta['cwl_start']
        )
        self.pg_data['cwl_input_json'] = os.path.join(
            self.workflow_meta['base_s3_loc'],
            os.path.basename(self.workflow_meta['cwl_input_json'])
        )
        self.pg_data['debug_path'] = self.workflow_meta['log_file']
