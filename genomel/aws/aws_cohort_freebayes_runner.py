'''GenoMEL-AWS Freebayes runner'''

import argparse
import utils.runner

def is_nat(pos):
    '''Checks that a value is a natural number.'''
    if int(pos) > 0:
        return int(pos)
    raise argparse.ArgumentTypeError('{} must be positive, non-zero'.format(pos))

def get_args():
    '''Loads the parser'''
    # Main parser
    parser = argparse.ArgumentParser(prog='GenoMEL-AWS Freebayes runner.', \
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
    required.add_argument('--freebayes_thread_count', \
                          required=True, \
                          type=is_nat, \
                          help='Threads used for Freebayes')
    required.add_argument('--number_of_chunks_for_freebayes', \
                          required=True, \
                          type=is_nat, \
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
    utils.runner.freebayes(args)
