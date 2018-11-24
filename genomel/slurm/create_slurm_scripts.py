'''GenoMEL-Bionimbus Protected Data Cloud SLURM scripts creator'''

import argparse
import utils.slurm

def get_args():
    '''Loads the parser'''
    # Main parser
    parser = argparse.ArgumentParser(prog='GenoMEL-Bionimbus Protected Data Cloud \
        SLURM scripts creator.')
    # Required parser
    required = parser.add_argument_group("Required input parameters")
    required.add_argument('--outdir', \
                          required=True, \
                          help='Script out directory')
    required.add_argument('--config_local', \
                          required=True, \
                          help='Local PSQL config file')
    required.add_argument('--input_table', \
                          required=True, \
                          help='PSQL input table')
    required.add_argument('--status_table', \
                          default=None, \
                          help='PSQL status table')
    required.add_argument('--pipeline', \
                          required=True, \
                          choices=['alignment', 'harmonization'], \
                          help='Choose the desired pipeline')
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Create scripts
    utils.slurm.create_scripts(args)
