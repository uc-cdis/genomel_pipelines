'''create new header with uniq readgroup id'''
import re
import os
import argparse

def create_new_header(old_header, aliquot_id):
    '''create new header'''
    with open(old_header, 'r') as fhandle:
        old_header = fhandle.readlines()
        for line in old_header:
            if not line.startswith('@RG'):
                with open('new_header', 'a') as ohandle:
                    ohandle.write(line)
            else:
                old_line = line.rstrip().split('\t')
                for tab in old_line:
                    if tab.startswith('ID:'):
                        old_rg = tab.replace('ID:', '')
                        new_rg = aliquot_id + '_' + old_rg
                        new_line = re.sub(
                            r"\b{}\t\b".format(old_rg),
                            "{}\t".format(new_rg),
                            line
                        )
                        with open('new_header', 'a') as ohandle:
                            ohandle.write(new_line)
    return os.path.abspath('new_header')

def get_args():
    '''Loads the parser'''
    # Main parser
    parser = argparse.ArgumentParser(prog='Fix header.', \
                                     add_help=False)
    # Required parser
    required = parser.add_argument_group("Required input parameters")
    required.add_argument('--old_header', \
                          required=True, \
                          help='Old header')
    required.add_argument('--aliquot_id', \
                           required=True, \
                           help='Aliquot id of the bam.')
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Run pipeline
    create_new_header(args.old_header, args.aliquot_id)
