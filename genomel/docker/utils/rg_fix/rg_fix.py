'''create new header with uniq readgroup id'''
import os
import sys
import argparse
import subprocess

def prepare_header_info(old_header, aliquot_id):
    '''prepare new header info'''
    new_header = dict()
    with open(old_header, 'r') as fhandle:
        old_header = fhandle.readlines()
        for line in old_header:
            if line.startswith('@RG'):
                rg_line = line.rstrip().split('\t')
                break
        for i in rg_line:
            if i.startswith('CN'):
                new_header['CN'] = i.replace('CN:', '')
            elif i.startswith('LB'):
                new_header['LB'] = i.replace('LB:', '')
            elif i.startswith('PL'):
                new_header['PL'] = i.replace('PL:', '')
            elif i.startswith('PU'):
                new_header['PU'] = i.replace('PU:', '')
            elif i.startswith('SM'):
                new_header['SM'] = i.replace('SM:', '')
            new_header['ID'] = aliquot_id
    return new_header

def run_command(cmd, logger=None, output=None, shell_var=False):
    '''Runs a subprocess'''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                             shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode
    if logger:
        logger.info(cmd)
        if output:
            with open(output, 'wt') as ohandle:
                ohandle.write(stdoutdata)
        else:
            for line in stdoutdata.split("\n"):
                logger.info(line)
        for line in stderrdata.split("\n"):
            logger.info(line)
    else:
        print cmd
        print stdoutdata
        print stderrdata
    return exit_code

def picard_cmd(header_dict, input_bam):
    '''cmd template'''
    base, ext = os.path.splitext(input_bam)
    output_bam = base + '.rg_fixed' + ext
    cmd_list = [
        'java',
        '-Xmx100G',
        '-XX:ParallelGCThreads=30',
        '-jar',
        '/opt/picard.jar',
        'AddOrReplaceReadGroups',
        'I={}'.format(input_bam),
        'O={}'.format(output_bam),
        'RGID={}'.format(header_dict['ID']),
        'RGLB={}'.format(header_dict['LB']),
        'RGPL={}'.format(header_dict['PL']),
        'RGPU={}'.format(header_dict['PU']),
        'RGSM={}'.format(header_dict['SM'])
    ]
    return cmd_list

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
    required.add_argument('--input_bam', \
                           required=True, \
                           help='Input bam.')
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Run pipeline
    header = prepare_header_info(args.old_header, args.aliquot_id)
    picard_exit = run_command(picard_cmd(header, args.input_bam))
    if picard_exit:
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'
