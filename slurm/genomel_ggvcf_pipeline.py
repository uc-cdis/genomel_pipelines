'''
Main wrapper script for Genotype GVCF workflow
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
import glob
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
    required.add_argument("--input_path", default=None, help="Path to pre-staged files")
    required.add_argument("--project", default=None, help="PROJECT, PDC project name.")
    required.add_argument("--s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for pipeline
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations.")
    required.add_argument("--refdir", required=True, help="Path to reference directory.")
    required.add_argument("--cwl", required=True, help="Path to Genomel Recalibration CWL workflow yaml.")
    required.add_argument("--s3dir", default="s3://", help="S3 dir for uploading output files.")

    required.add_argument('--java_heap', required=True, help='Java heap memory limit.')
    required.add_argument('--thread_count', type=is_nat, default=8, help='Threads count.')

    required.add_argument('--chunk', type=is_nat, default=30, help='Chunk order')
    required.add_argument('--intervals', type=is_nat, default=30, help='Number of total regions')

    return parser.parse_args()


def run_pipeline(args, statusclass, metricsclass):
    '''
    Executes the CWL pipeline and record status/metrics tables
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)
    
    # Generate a uuid
    output_id = uuid.uuid4()
    # Get hostname
    hostname = socket.gethostname()
    # Get datetime start
    datetime_start = str(datetime.datetime.now())
    
    # Create directory structure
    jobdir = tempfile.mkdtemp(prefix="ggvcf_%s_" % str(output_id), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=jobdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=jobdir)
    resultdir = tempfile.mkdtemp(prefix="result_", dir=jobdir)
    refdir = args.refdir
    
    # Setup logger
    log_file = os.path.join(resultdir, "%s.genomel.ggvcf.cwl.log" % str(output_id))
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
    reference_intervals   = os.path.join(refdir, reference_data["reference_intervals"])     
    postgres_config       = os.path.join(refdir, reference_data["pg_config"])

    # Calculating region according to chunk
    chunked_intervals = utils.get_interval_region(reference_intervals, workdir, args.chunk, args.intervals)

    # Logging pipeline info
    cwl_version    = reference_data["cwl_version"]
    docker_version = reference_data["docker_version"]
    logger.info("cwl_version: %s" % (cwl_version))
    logger.info("docker_version: %s" % (docker_version))
    
    # Define output
    output_gvcf = os.path.join(workdir, os.path.basename(input_bam)).replace('.bam', '.vcf.gz')

    # Get input files
    file_array = []
    for f in glob.glob(args.input_path + '/*.g.vcf.gz')
        file_array.append({"class": "File", "path": f})
    
    # Create input json
    input_json_file = os.path.join(resultdir, '{0}.genomel.hc.inputs.json'.format(str(output_id)))
    input_json_data = {
      "java_opts": args.java_heap,    
      "input_vcf_path": file_array,
      "reference_fasta_path": {"class": "File", "path": reference_fasta_path},
      "interval_file_path": {"class": "File", "path": chunked_intervals}, 
      "output_vcf_name": os.path.basename(output_gvcf)      
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
