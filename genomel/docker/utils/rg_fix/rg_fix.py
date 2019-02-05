'''create new header with uniq readgroup id'''
import re
import os
import argparse

def create_new_header(old_header, problem_rg, new_rg):
    '''create new header'''
    with open(old_header, 'r') as fhandle:
        old_header = fhandle.readlines()
        for line in old_header:
            if not line.startswith('@RG'):
                with open('new_header', 'a') as ohandle:
                    ohandle.write(line)
            else:
                for o_rg, n_rg in zip(problem_rg, new_rg):
                    new_line = re.sub(r"\b{}\t\b".format(o_rg), "{}\t".format(n_rg), line)
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
    required.add_argument('--problem_rg', \
                           required=True, \
                           nargs='+', \
                           help='Problematic read group ids.')
    required.add_argument('--new_rg', \
                           required=True, \
                           nargs='+', \
                           help='New read group ids.')
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Run pipeline
    create_new_header(args.old_header, args.problem_rg, args.new_rg)
