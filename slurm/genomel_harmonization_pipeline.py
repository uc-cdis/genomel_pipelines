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
    required.add_argument("--input_id", default=None, help="INPUT_ID, internal production id.")
    required.add_argument("--project", default=None, help="PROJECT, project name.")
    required.add_argument("--input_table", default=None, help="Input table name")    
    required.add_argument("--md5", default=None, help="MD5, md5 of input file.")
    required.add_argument("--s3_url", default=None, help="S3_URL, s3 url of the input.")
    required.add_argument("--s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for pipeline
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations.")
    required.add_argument("--refdir", required=True, help="Path to reference directory.")
    required.add_argument("--cwl", required=True, help="Path to Genomel Recalibration CWL workflow yaml.")
    required.add_argument("--bam_s3dir", default="s3://", help="S3 dir for uploading bam output files.")
    required.add_argument("--fastq_s3dir", default="s3://", help="S3 dir for uploading fastq output files.")
    required.add_argument('--output_id', required=True, help='UUID for the output')

    required.add_argument('--thread_count', type=is_nat, default=8, help='Threads count.')

    return parser.parse_args()


def run_pipeline(args, harmo_statusclass, harmo_metricsclass):
    '''
    Executes the CWL pipeline and record status/metrics tables
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)
    
    # Get output uuid
    job_id = args.output_id
    # Get hostname
    hostname = socket.gethostname()
    # Get datetime start
    datetime_start = str(datetime.datetime.now())
    
    # Create directory structure
    jobdir = tempfile.mkdtemp(prefix="harmonization_%s_" % str(job_id), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=jobdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=jobdir)
    resultdir = tempfile.mkdtemp(prefix="result_", dir=jobdir)
    refdir = args.refdir
    
    # Setup logger
    log_file = os.path.join(resultdir, "%s.harmonization.cwl.log" % str(job_id))
    logger = utils.pipeline.setup_logging(logging.INFO, str(job_id), log_file)
    
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
    reference_indel_vcf   = os.path.join(refdir, reference_data["reference_indel_vcf"])
    reference_snp_vcf     = os.path.join(refdir, reference_data["reference_snp_vcf"])    
    postgres_config       = os.path.join(refdir, reference_data["pg_config"])
    
    # Logging pipeline info
    cwl_version    = reference_data["cwl_version"]
    docker_version = reference_data["docker_version"]
    logger.info("cwl_version: %s" % (cwl_version))
    logger.info("docker_version: %s" % (docker_version))
    
    # Download input bam
    input_url = args.s3_url
    input_bam = os.path.join(inputdir, os.path.basename(input_url))
    project_s3_profile = args.s3_profile
    project_s3_endpoint_url = args.s3_endpoint
    download_exit_code = utils.s3.aws_s3_get(logger, input_url, inputdir,
                                             project_s3_profile, project_s3_endpoint_url, recursive=False)

    download_end_time = time.time()
    download_time = download_end_time - cwl_start
    if not (download_exit_code != 0 or str(utils.pipeline.get_md5(input_bam)) != args.md5):
        logger.info("Download input %s successfully in %s, and md5 matches. Input bam is %s." % (args.input_id, download_time, input_bam))
    else:
        cwl_elapsed = download_time
        datetime_end = str(datetime.datetime.now())
        engine = postgres.utils.get_db_engine(postgres_config)
        postgres.utils.set_download_error(download_exit_code, logger, engine, args.project,
                                          job_id, [args.input_id], args.input_table, job_id,
                                          datetime_start, datetime_end,
                                          hostname, cwl_version, docker_version,
                                          download_time, cwl_elapsed, statusclass, metricsclass)

        # Exit
        sys.exit(download_exit_code)


    # Create input json
    input_json_file = os.path.join(resultdir, '{0}.genomel.harmonization.inputs.json'.format(str(job_id)))
    input_json_data = {
        "input_bam_path": {"class": "File", "path": input_bam},
        "reference_seq": {"class": "File", "path": reference_fasta_path},   
        "workflow_nthreads": args.thread_count,
        "workflow_end_mode": args.end_mode,
        "trimmomatic_java_opts": args.java_heap,
        "trimmomatic_phred": args.phred,
        "trimmomatic_input_adapters_file": {"class": "File", "path": adapters_file},
        "trimmomatic_illuminaclip": args.illuminaclip,
        "trimmomatic_slidingwindow": args.slidingwindow,
        "trimmomatic_leading": args.leading,
        "trimmomatic_trailing": args.trailing,
        "trimmomatic_minlen": args.minlen,
        "novoalign_dbname": {"class": "File", "path": reference_database},
        "novoalign_format": args.format,
        "novoalign_length": args.length,
        "novoalign_output_format": args.output_format
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
           "--relax-path-checks", 
           "--tmpdir-prefix", inputdir,
           "--tmp-outdir-prefix", workdir,
           args.cwl,
           input_json_file]
    cwl_exit = utils.pipeline.run_command(cmd, logger)
    cwl_failure = False
    if cwl_exit:
        cwl_failure = True

    # Calculate elapsed time
    cwl_end = time.time()
    cwl_elapsed = cwl_end - cwl_start
    logger.info("datetime_end: %s" % (str(datetime.datetime.now())))

    # Get metrics info
    time_metrics = utils.pipeline.get_time_metrics(log_file)

    # Getting output files
    output_fastqr1_files = glob.glob(workdir + '/*_1.fq.gz')
    fqr1_md5sums = []
    fqr1_file_sizes = []
    fqr1_filenames = []
    fqr2_md5sums = []
    fqr2_file_sizes = []
    fqr2_filenames = []
    bam_md5sums = []
    bam_file_sizes = []
    bam_filenames = []
    upload_start = time.time()
    for fastqr1 in output_fastqr1_files:
        # Get md5 and file sizes     
        fastqr1_filename = os.path.basename(fastqr1)
        fastqr2_filename = os.path.basename(fastqr1).replace('_1.fq.gz', '_2.fq.gz')
        bam_filename     = os.path.basename(fastqr1).replace('_1.fq.gz', '.srt.LENIENT.duplicate_removed.paired.nophix.SILENT.duplicate_removed.bam')
        bai_filename     = os.path.basename(fastqr1).replace('_1.fq.gz', '.srt.LENIENT.duplicate_removed.paired.nophix.SILENT.duplicate_removed.bai')
        output_fastqr1 = os.path.join(workdir, fastqr1_filename)
        output_fastqr2 = os.path.join(workdir, fastqr2_filename)
        output_bam     = os.path.join(workdir, bam_filename)
        output_bai     = os.path.join(workdir, bai_filename)

        # Append filenames
        fqr1_filenames.append(fastqr1_filename)
        fqr2_filenames.append(fastqr2_filename)
        bam_filenames.append(bam_filename)

        # MD5SUMS
        fqr1_md5sums.append(utils.pipeline.get_md5(output_fastqr1))
        fqr2_md5sums.append(utils.pipeline.get_md5(output_fastqr2))
        bam_md5sums.append(utils.pipeline.get_md5(output_bam))
        
        # File sizes
        fqr2_file_sizes.append(utils.pipeline.get_file_size(output_fastqr2))
        bam_md5sums.append(utils.pipeline.get_md5(output_bam))
        bam_file_sizes.append(utils.pipeline.get_file_size(output_fastqr1))

        # Upload FASTQ outputs
        os.chdir(jobdir)
        upload_dir_location = os.path.join(args.fastq_s3dir, str(job_id))
        upload_fastq1_location = os.path.join(upload_dir_location, os.path.basename(output_fastqr1))   
        upload_fastq2_location = os.path.join(upload_dir_location, os.path.basename(output_fastqr2))
        logger.info("Uploading workflow FASTQ output to %s" % (upload_dir_location))
        upload_exit  = utils.s3.aws_s3_put(logger, upload_fastq1_location, output_fastqr1, args.s3_profile, args.s3_endpoint, recursive=False)
        upload_exit  = utils.s3.aws_s3_put(logger, upload_fastq2_location, output_fastqr2, args.s3_profile, args.s3_endpoint, recursive=False)
        
        # Upload BAM/BAI outputs
        os.chdir(jobdir)
        upload_dir_location = os.path.join(args.bam_s3dir, str(job_id))
        upload_bam_location = os.path.join(upload_dir_location, os.path.basename(output_bam))   
        upload_bai_location = os.path.join(upload_dir_location, os.path.basename(output_bai))
        logger.info("Uploading workflow BAM output to %s" % (upload_dir_location))
        upload_exit  = utils.s3.aws_s3_put(logger, upload_bam_location, output_bam, args.s3_profile, args.s3_endpoint, recursive=False)
        upload_exit  = utils.s3.aws_s3_put(logger, upload_bai_location, output_bai, args.s3_profile, args.s3_endpoint, recursive=False)

        # Establish connection with database
        engine = postgres.utils.get_db_engine(postgres_config)
        
        # Calculate times
        cwl_end = time.time()
        upload_time = cwl_end - upload_start
     
         # Get status info
        logger.info("Get status/metrics info")
        status, loc = postgres.status.get_status(upload_exit, cwl_exit, upload_bam_location, upload_dir_location, logger)           

        file_id = uuid.uuid4()
        logger.info("Updating status for %s" % bam_filename) 
        postgres.utils.add_pipeline_status(engine, args.project, file_id, [args.input_id], args.input_table, job_id,
                                           status, loc, datetime_start, datetime_end,
                                           bam_md5sums[idx], bam_file_sizes[idx], hostname, cwl_version, docker_version, harmo_statusclass)
        # Set metrics table
        logger.info("Updating metrics for %s" % bam_filename)
        postgres.utils.add_pipeline_metrics(engine, file_id, [args.input_id], args.input_table, download_time,
                                            upload_time, args.thread_count, cwl_elapsed,
                                            time_metrics['system_time'],
                                            time_metrics['user_time'],
                                            time_metrics['wall_clock'],
                                            time_metrics['percent_of_cpu'],
                                            time_metrics['maximum_resident_set_size'],
                                            status, harmo_metricsclass)
    

    # Remove job directories, upload final log file
    logger.info("Uploading main log file")
    utils.s3.aws_s3_put(logger, upload_dir_location + '/' + os.path.basename(log_file), log_file, args.s3_profile, args.s3_endpoint, recursive=False)
    utils.pipeline.remove_dir(jobdir)



if __name__ == '__main__':
    
    # Get args
    args = get_args()
    project = args.project.lower()
    
    # Setup postgres classes for tables
    class HarmonizationStatus(postgres.mixins.StatusTypeMixin, postgres.utils.Base):
        __tablename__ = 'genomel_harmonization_cwl_status'
    class HarmonizationMetrics(postgres.mixins.MetricsTypeMixin, postgres.utils.Base):
        __tablename__ = 'genomel_harmonization_cwl_metrics'
    
    # Run pipeline
    run_pipeline(args, HarmonizationStatus, HarmonizationMetrics)