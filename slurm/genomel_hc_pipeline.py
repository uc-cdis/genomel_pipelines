'''
Main wrapper script for Genomel Haplotype caller workflow
'''
import os
import time
import argparse
import logging
import sys
import uuid
import tempfile
import utils.s3
import utils.pipeline
import datetime
import socket
import json

import postgres.status
import postgres.utils
import postgres.mixins

from sqlalchemy.exc import NoSuchTableError

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

def get_args():
    '''
    Loads the parser
    '''
    # Main parser
    parser = argparse.ArgumentParser(description="Genomel Haplotype caller Pipeline")
    # Args
    required = parser.add_argument_group("Required input parameters")
    # Metadata from input table
    required.add_argument("--input_id", default=None, help="INPUT_ID, internal production id.")
    required.add_argument("--project", default=None, help="PROJECT, PDC project name.")
    required.add_argument("--md5", default=None, help="MD5, md5 of input file.")
    required.add_argument("--s3_url", default=None, help="S3_URL, s3 url of the input.")
    required.add_argument("--s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for pipeline
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations.")
    required.add_argument("--refdir", required=True, help="Path to reference directory.")
    required.add_argument("--cwl", required=True, help="Path to Genomel Recalibration CWL workflow yaml.")
    required.add_argument("--s3dir", default="s3://", help="S3 dir for uploading output files.")
    required.add_argument('--output_id', required=True, help='UUID for the output')

    required.add_argument('--java_heap', required=True, help='Java heap memory limit.')
    required.add_argument('--thread_count', type=is_nat, default=8, help='Threads count.')

    return parser.parse_args()


def run_pipeline(args, statusclass, metricsclass):
    '''
    Executes the CWL pipeline and record status/metrics tables
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)
    
    # Get output uuid
    output_id = args.output_id
    # Get hostname
    hostname = socket.gethostname()
    # Get datetime start
    datetime_start = str(datetime.datetime.now())
    
    # Create directory structure
    jobdir = tempfile.mkdtemp(prefix="hc_%s_" % str(output_id), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=jobdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=jobdir)
    resultdir = tempfile.mkdtemp(prefix="result_", dir=jobdir)
    refdir = args.refdir
    
    # Setup logger
    log_file = os.path.join(resultdir, "%s.genomel.hc.cwl.log" % str(output_id))
    logger = utils.pipeline.setup_logging(logging.INFO, str(output_id), log_file)
    
    # Logging inputs
    logger.info("hostname: %s" % (hostname))
    logger.info("input_id: %s" % (args.input_id))
    logger.info("project: %s" % (args.project))
    logger.info("md5: %s" % (args.md5))
    logger.info("datetime_start: %s" % (datetime_start))
    
    # Setup start point
    cwl_start = time.time()
    
    # Getting refs
    logger.info("getting resources")
    reference_data        = utils.pipeline.load_reference_json('etc/reference.json')
    reference_fasta_path  = os.path.join(refdir, reference_data["reference_fasta"])   
    reference_dbsnp       = os.path.join(refdir, reference_data["reference_dbsnp"]) 
    reference_intervals   = os.path.join(refdir, reference_data["reference_intervals"])     
    postgres_config       = os.path.join(refdir, reference_data["pg_config"])
    
    # Logging pipeline info
    cwl_version    = reference_data["cwl_version"]
    docker_version = reference_data["docker_version"]
    logger.info("cwl_version: %s" % (cwl_version))
    logger.info("docker_version: %s" % (docker_version))
    
    # Download input bam and index
    input_url = args.s3_url
    input_bam = os.path.join(inputdir, os.path.basename(input_url))
    input_index_url = input_url.replace('.bam','.bai')
    project_s3_profile = args.s3_profile
    project_s3_endpoint_url = args.s3_endpoint
    download_exit_code = utils.s3.aws_s3_get(logger, input_url, inputdir,
                                             project_s3_profile, project_s3_endpoint_url, recursive=False)
    download_exit_code = utils.s3.aws_s3_get(logger, input_index_url, inputdir,
                                             project_s3_profile, project_s3_endpoint_url, recursive=False)

    download_end_time = time.time()
    download_time = download_end_time - cwl_start
    if not (download_exit_code != 0 or str(utils.pipeline.get_md5(input_bam)) != args.md5):
        logger.info("Download input %s successfully in %s, and md5 matches. Input bam is %s." % (args.input_id, download_time, input_bam))
    else:
        cwl_elapsed = download_time
        datetime_end = str(datetime.datetime.now())
        engine = postgres.utils.get_db_engine(postgres_config)
        postgres.utils.set_download_error(download_exit_code, logger, engine,
                                          output_id, [args.input_id], output_id,
                                          datetime_start, datetime_end,
                                          hostname, cwl_version, docker_version,
                                          download_time, cwl_elapsed, statusclass, metricsclass)
        # Exit
        sys.exit(download_exit_code)

    # Define output
    output_gvcf = os.path.join(workdir, str(output_id) + '.g.vcf.gz')

    # Create input json
    input_json_file = os.path.join(resultdir, '{0}.genomel.hc.inputs.json'.format(str(output_id)))
    input_json_data = {
      "java_opts": args.java_heap,    
      "input_bam_path": {"class": "File", "path": input_bam},
      "reference_fasta_path": {"class": "File", "path": reference_fasta_path},
      "reference_snp_path": {"class": "File", "path": reference_dbsnp},
      "interval_file_path": {"class": "File", "path": reference_intervals}, 
      "output_gvcf_name": os.path.basename(output_gvcf),
      "thread_count": str(args.thread_count)       
    }
    with open(input_json_file, 'wt') as o:
        json.dump(input_json_data, o, indent=4)
    logger.info("Preparing input json: %s" % (input_json_file))
    
    # Run CWL
    os.chdir(workdir)
    logger.info('Running CWL workflow')
    cmd = ['/usr/bin/time', '-v',
           '/home/ubuntu/.virtualenvs/p2/bin/cwltool',
           "--debug",
           "--tmpdir-prefix", inputdir,
           "--tmp-outdir-prefix", workdir,
           args.cwl,
           input_json_file]
    cwl_exit = utils.pipeline.run_command(cmd, logger)
    cwl_failure = False
    if cwl_exit:
        cwl_failure = True

    # Get md5 and file size
    md5 = utils.pipeline.get_md5(output_gvcf)
    file_size = utils.pipeline.get_file_size(output_gvcf)
    
    # Upload output
    upload_start = time.time()
    upload_dir_location = os.path.join(args.s3dir, str(output_id))
    upload_gvcf_location = os.path.join(upload_dir_location, os.path.basename(output_gvcf))    
    logger.info("Uploading workflow output to %s" % (upload_gvcf_location))
    upload_exit  = utils.s3.aws_s3_put(logger, upload_gvcf_location, output_gvcf, args.s3_profile, args.s3_endpoint, recursive=False)

    # Establish connection with database
    engine = postgres.utils.get_db_engine(postgres_config)
    
    # Calculate times
    cwl_end = time.time()
    upload_time = cwl_end - upload_start
    cwl_elapsed = cwl_end - cwl_start
    datetime_end = str(datetime.datetime.now())
    logger.info("datetime_end: %s" % (datetime_end))
    
    # Get status info
    logger.info("Get status/metrics info")
    status, loc = postgres.status.get_status(upload_exit, cwl_exit, upload_gvcf_location, upload_dir_location, logger)
    
    # Get metrics info
    time_metrics = utils.pipeline.get_time_metrics(log_file)
    
    # Set status table
    logger.info("Updating status")
    postgres.utils.add_pipeline_status(engine, output_id, [args.input_id], output_id,
                                       status, loc, datetime_start, datetime_end,
                                       md5, file_size, hostname, cwl_version, docker_version, statusclass)
    # Set metrics table
    logger.info("Updating metrics")
    postgres.utils.add_pipeline_metrics(engine, output_id, [args.input_id], download_time,
                                        upload_time, args.thread_count, cwl_elapsed,
                                        time_metrics['system_time'],
                                        time_metrics['user_time'],
                                        time_metrics['wall_clock'],
                                        time_metrics['percent_of_cpu'],
                                        time_metrics['maximum_resident_set_size'],
                                        status, metricsclass)
    
    # Remove job directories, upload final log file
    logger.info("Uploading main log file")
    utils.s3.aws_s3_put(logger, upload_dir_location + '/' + os.path.basename(log_file), log_file, args.s3_profile, args.s3_endpoint, recursive=False)
    utils.pipeline.remove_dir(jobdir)



if __name__ == '__main__':
    
    # Get args
    args = get_args()
    project = args.project.lower()
    
    # Setup postgres classes for tables
    class CallerStatus(postgres.mixins.StatusTypeMixin, postgres.utils.Base):
        __tablename__ = project + '_hc_cwl_status'
    class CallerMetrics(postgres.mixins.MetricsTypeMixin, postgres.utils.Base):
        __tablename__ = project + '_hc_cwl_metrics'
    
    # Run pipeline
    run_pipeline(args, CallerStatus, CallerMetrics)
