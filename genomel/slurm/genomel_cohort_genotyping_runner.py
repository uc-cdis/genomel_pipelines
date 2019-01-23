'''GenoMEL-Bionimbus Protected Data Cloud SLURM runner'''

import argparse
import utils.workflow

def get_args():
    '''Loads the parser'''
    # Main parser
    parser = argparse.ArgumentParser(prog='GenoMEL-Bionimbus Protected Data Cloud SLURM runner.', \
                                     add_help=False)
    # Required parser
    required = parser.add_argument_group("Required input parameters")
    required.add_argument('--basedir', \
                          required=True, \
                          help='Base local work directory')
    required.add_argument('--project', \
                          required=True, \
                          help='Project')
    required.add_argument('--batch_id', \
                          required=True, \
                          help='Batch id')
    required.add_argument('--job_uuid', \
                          required=True, \
                          help='Job uuid')
    required.add_argument('--input_table', \
                          required=True, \
                          help='PSQL input table')
    required.add_argument('--psql_conf', \
                          required=True, \
                          help='Local PSQL config file')
    required.add_argument('--gvcf_files_manifest', \
                          required=True, \
                          help='Manifest of all gvcf files')
    required.add_argument('--gatk4_genotyping_thread_count', \
                          required=True, \
                          help='Threads used for GATK4 genotyping')
    required.add_argument('--number_of_chunks_for_gatk', \
                          required=True, \
                          help='Number of chunks for GATK4 on each node')
    required.add_argument('--bam_files_manifest', \
                          required=True, \
                          help='Manifest of all bam files')
    required.add_argument('--freebayes_thread_count', \
                          required=True, \
                          help='Threads used for Freebayes')
    required.add_argument('--number_of_chunks_for_freebayes', \
                          required=True, \
                          help='Number of chunks for Freebayes on each node')
    required.add_argument('--upload_s3_bucket', \
                          required=True, \
                          help='S3 bucket for uploads')
    required.add_argument('--cromwell_jar_path', \
                          required=True, \
                          help='Cromwell jar path')                          
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Run pipeline
    utils.workflow.run_cohort_genotyping(args)
