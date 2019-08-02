'''GenoMEL-Bionimbus Protected Data Cloud SLURM runner'''

import argparse
import utils.workflow

def is_nat(pos):
    '''Checks that a value is a natural number.'''
    if int(pos) > 0:
        return int(pos)
    raise argparse.ArgumentTypeError('{} must be positive, non-zero'.format(pos))

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
    required.add_argument('--job_uuid', \
                          required=True, \
                          help='Job uuid')
    required.add_argument('--psql_conf', \
                          required=True, \
                          help='Local PSQL config file')
    required.add_argument('--bed', \
                          required=True, \
                          help='Bed file.')
    required.add_argument('--cwlwf', \
                          required=True, \
                          help='CWL workflow path')
    required.add_argument('--vcf', \
                          required=True, \
                          help='Input VCF file.')
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Run pipeline
    utils.workflow.run_fbc(args)
