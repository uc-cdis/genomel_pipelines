'''
Main wrapper script for Genomel Recalibration workflow
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
    parser = argparse.ArgumentParser(description="Genomel Recalibration Pipeline")
    # Args
    required = parser.add_argument_group("Required input parameters")
    # Metadata from input table
    required.add_argument("--input_r1_id", default=None, help="INPUT_ID for read 1")
    required.add_argument("--input_r2_id", default=None, help="INPUT_ID for read 2")   
    required.add_argument("--project", default=None, help="PROJECT, PDC project name.")
    required.add_argument("--r1_md5", default=None, help="MD5, md5 of read 1 file.")
    required.add_argument("--r2_md5", default=None, help="MD5, md5 of read 2 file.")    
    required.add_argument("--s3_url_r1", default=None, help="S3_URL, s3 url of the read 1 input.")
    required.add_argument("--s3_url_r2", default=None, help="S3_URL, s3 url of the read 2 input.")   
    required.add_argument("--s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--s3_endpoint", required=True, help="S3 endpoint url for project tenant.")

    # Parameters for pipeline
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations.")
    required.add_argument("--refdir", required=True, help="Path to reference directory.")
    required.add_argument("--cwl", required=True, help="Path to Genomel Recalibration CWL workflow yaml.")
    required.add_argument("--s3dir", default="s3://", help="S3 dir for uploading output files.")
    required.add_argument('--output_id', required=True, help='UUID for the output')
    required.add_argument('--thread_count', type=is_nat, default=8, help='Threads count.')
    required.add_argument('--java_heap', required=True, help='Jave heap memory')

    # Tools parameters
    required.add_argument('--end_mode', default="PE", help="End mode in alignment")
    required.add_argument('--phred', default="33", help="Trimmomatic phred")
    required.add_argument('--illuminaclip', default="2:30:12", help="Trimmomatic Illumina clip lengths")
    required.add_argument('--slidingwindow', default="4:15", help="Trimmomatic sliding windows length")    
    required.add_argument('--leading', default="12", help="Trimmomatic leading")
    required.add_argument('--trailing', default="12", help="Trimmomatic trailing")
    required.add_argument('--minlen', default="36", help="Trimmomatic minimal acceptable length")
    required.add_argument('--format', default="ILM1.8", help="Alignment technology format")    
    required.add_argument('--length', default="300,125", help="Alignment read length")
    required.add_argument('--output_format', default="SAM", help="Alignment output format")

    return parser.parse_args()


def run_pipeline(args, statusclass, metricsclass):
    '''
    Executes the CWL pipeline and record status/metrics tables
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)
    
    # Get hostname
    hostname = socket.gethostname()
    # Get datetime start
    datetime_start = str(datetime.datetime.now())
    
    # Create directory structure
    jobdir = tempfile.mkdtemp(prefix="alignment_%s_" % str(args.output_id), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=jobdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=jobdir)
    resultdir = tempfile.mkdtemp(prefix="result_", dir=jobdir)
    refdir = args.refdir
    
    # Setup logger
    log_file = os.path.join(resultdir, "%s.alignment.cwl.log" % str(args.output_id))
    logger = utils.pipeline.setup_logging(logging.INFO, str(args.output_id), log_file)
    
    # Logging inputs
    logger.info("hostname: %s" % (hostname))
    logger.info("input_ids: %s %s" % (args.input_r1_id, args.input_r2_id))
    logger.info("project: %s" % (args.project))
    logger.info("md5: %s %s" % (args.r1_md5, args.r2_md5))
    logger.info("datetime_start: %s" % (datetime_start))
    
    # Setup start point
    cwl_start = time.time()
    
    # Getting refs
    logger.info("getting resources")
    reference_data        = utils.pipeline.load_reference_json('etc/reference.json')
    reference_fasta_path  = os.path.join(refdir, reference_data["reference_fasta"])
    reference_database    = os.path.join(refdir, reference_data["reference_database"]) 
    adapters_file         = os.path.join(refdir, reference_data["adapters_file"])     
    postgres_config       = os.path.join(refdir, reference_data["pg_config"])
    
    # Logging pipeline info
    cwl_version    = reference_data["cwl_version"]
    docker_version = reference_data["docker_version"]
    logger.info("cwl_version: %s" % (cwl_version))
    logger.info("docker_version: %s" % (docker_version))
    
    # Download input reads
    project_s3_profile = args.s3_profile
    project_s3_endpoint_url = args.s3_endpoint
    reads   = [args.input_r1_id, args.input_r2_id]
    s3_urls = [args.s3_url_r1, args.s3_url_r2]
    md5sums = [args.r1_md5, args.r2_md5]
    input_files = []
    for r in range(0,2):
        input_url = s3_urls[r]
        input_files[r] = os.path.join(inputdir, os.path.basename(input_url))
        download_exit_code = utils.s3.aws_s3_get(logger, input_url, inputdir,
                                             project_s3_profile, project_s3_endpoint_url, recursive=False)


        if not (download_exit_code != 0 or str(utils.pipeline.get_md5(input_files[r])) != md5sums[r]):
            logger.info("Download input %s successfully in %s, and md5 matches. Input bam is %s." % (reads[r], download_time, input_files[r]))
        else:
            cwl_elapsed = download_time
            datetime_end = str(datetime.datetime.now())
            engine = postgres.utils.get_db_engine(postgres_config)
            postgres.utils.set_download_error(download_exit_code, logger, engine,
                                              args.output_id, [args.input_files[r]], args.output_id,
                                              datetime_start, datetime_end,
                                              hostname, cwl_version, docker_version,
                                              download_time, cwl_elapsed, statusclass, metricsclass)
        # Exit
        sys.exit(download_exit_code)


    download_end_time = time.time()
    download_time = download_end_time - cwl_start

    # Define output file
    output_name = os.path.basename(input_files[0]).replace('_R1_001.fastq.gz', '')   
    sample_id = output_name.split('_')[0]
    output_bam = os.path.join(workdir, output_name + '.bam')
    output_bai = output_bam + '.bai'
 

    # Create input json
    input_json_file = os.path.join(resultdir, '{0}.genomel.alignment.inputs.json'.format(str(args.output_id)))
    input_json_data = {
        "workflow_nthreads": args.thread_count,
        "workflow_end_mode": args.end_mode,
        "trimmomatic_java_opts": args.java_heap,
        "trimmomatic_phred": args.phred,
        "trimmomatic_input_read1_fastq_file": {"class": "File", "path": input_files[0]},
        "trimmomatic_input_read2_fastq_file": {"class": "File", "path": input_files[1]},
        "trimmomatic_input_adapters_file": {"class": "File", "path": adapters_file},
        "trimmomatic_illuminaclip": args.illuminaclip,
        "trimmomatic_slidingwindow": args.slidingwindow,
        "trimmomatic_leading": args.leading,
        "trimmomatic_trailing": args.trailing,
        "trimmomatic_minlen": args.minlen,
        "novoalign_dbname": {"class": "File", "path": reference_database},
        "novoalign_format": args.format,
        "novoalign_length": args.length,
        "novoalign_output_format": args.output_format,
        "novoalign_readgroup": "@RG\tCN:CGR\tPL:ILLUMINA\tID:%s_HQ_paired\tSM:%s\tPU:%s_HQ_paired\tLB:N/A" % (output_name, sample_id, output_name),
        "novoalign_output_name": basename(output_bam),
        "reference_seq": { "class": "File", "path": reference_fasta_path}
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
    md5 = utils.pipeline.get_md5(output_bam)
    file_size = utils.pipeline.get_file_size(output_bam)
    
    # Upload output
    upload_start = time.time()
    os.chdir(jobdir)
    upload_dir_location = os.path.join(args.s3dir, str(args.output_id))
    upload_bam_location = os.path.join(upload_dir_location, os.path.basename(output_bam))    
    upload_bai_location = os.path.join(upload_dir_location, os.path.basename(output_bai))
    logger.info("Uploading workflow output to %s" % (upload_bam_location))
    upload_exit  = utils.s3.aws_s3_put(logger, upload_bam_location, output_bam, args.s3_profile, args.s3_endpoint, recursive=False)
    upload_exit  = utils.s3.aws_s3_put(logger, upload_bai_location, output_bai, args.s3_profile, args.s3_endpoint, recursive=False)
    
    
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
    status, loc = postgres.status.get_status(upload_exit, cwl_exit, upload_bam_location, upload_dir_location, logger)
    
    # Get metrics info
    time_metrics = utils.pipeline.get_time_metrics(log_file)
    
    # Set status table
    logger.info("Updating status")
    postgres.utils.add_pipeline_status(engine, args.output_id, [args.input_r1_id,args.input_r2_id], args.output_id,
                                       status, loc, datetime_start, datetime_end,
                                       md5, file_size, hostname, cwl_version, docker_version, statusclass)
    # Set metrics table
    logger.info("Updating metrics")
    postgres.utils.add_pipeline_metrics(engine, args.output_id, [args.input_r1_id,args.input_r2_id], download_time,
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
    class RecalibrationStatus(postgres.mixins.StatusTypeMixin, postgres.utils.Base):
        __tablename__ = project + '_alignment_cwl_status'
    class RecalibrationMetrics(postgres.mixins.MetricsTypeMixin, postgres.utils.Base):
        __tablename__ = project + '_alignment_cwl_metrics'
    
    # Run pipeline
    run_pipeline(args, RecalibrationStatus, RecalibrationMetrics)
