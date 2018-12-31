#!/usr/bin/env python
'''Internal multithreading for Freebayes, GenoMEL-PDC'''

import sys
import argparse
import subprocess
import string
from functools import partial
from multiprocessing.dummy import Pool, Lock

def is_nat(pos):
    '''Checks that a value is a natural number.'''
    if int(pos) > 0:
        return int(pos)
    raise argparse.ArgumentTypeError('{} must be positive, non-zero'.format(pos))

def do_pool_commands(cmd, lock=Lock(), shell_var=True):
    '''run pool commands'''
    try:
        output = subprocess.Popen(cmd, shell=shell_var, \
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_stdout, output_stderr = output.communicate()
        with lock:
            print 'running: {}'.format(cmd)
            print output_stdout
            print output_stderr
    except BaseException:
        print "command failed {}".format(cmd)
    return output.wait()

def multi_commands(cmds, thread_count, shell_var=True):
    '''run commands on number of threads'''
    pool = Pool(int(thread_count))
    output = pool.map(partial(do_pool_commands, shell_var=shell_var), cmds)
    return output

def get_region(bed_lines, region_cmd):
    '''
    create chrX:Y-Z format region upon splitted bed
    bed_lines is lines in bed file
    region_cmd should be a list
    '''
    intm_region = dict()
    for i in bed_lines:
        chrom, start, end = i.split('\t')
        if chrom in intm_region:
            if intm_region[chrom]['start'] > int(start):
                intm_region[chrom]['start'] = int(start)
            if intm_region[chrom]['end'] < int(end.rstrip()):
                intm_region[chrom]['end'] = int(end.rstrip())
        else:
            intm_region[chrom] = {
                'start': int(start),
                'end': int(end.rstrip())
            }
    for chrom, pos in intm_region.items():
        region_str = '{}:{}-{}'.format(chrom, pos['start'], pos['end'])
        region_cmd.append(region_str)
    return region_cmd

def prepare_region(bed_file, nchunks):
    '''prepare N (N = nchunks) child region upon bed input'''
    bed_region = []
    with open(bed_file, 'r') as fhandle:
        lines = fhandle.readlines()
        nline = len(lines)/nchunks + 1
        child = [lines[i:i + nline] for i in xrange(0, len(lines), nline)]
        for chunk in child:
            get_region(chunk, bed_region)
    return bed_region

def freebayes_template(cmd_dict, nchunks):
    '''cmd template'''
    cmd_list = [
        '/opt/freebayes/bin/freebayes',
        '-L', '${BAM_LIST}',
        '-f', '${REF}',
        '-r', '${BED}',
        '-v', '${OUTPUT}',
        '--use-best-n-alleles', '6'
    ]
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for i, region in enumerate(prepare_region(cmd_dict['bed_file'], nchunks)):
        output = cmd_dict['job_uuid'] + '.' + str(i) + '.vcf'
        cmd = template.substitute(
            dict(
                BAM_LIST=cmd_dict['bam_list'],
                REF=cmd_dict['ref'],
                BED=region,
                OUTPUT=output
            )
        )
        yield cmd

def main():
    '''main'''
    parser = argparse.ArgumentParser('GenoMEL-PDC Freebayes.')
    # Required flags.
    parser.add_argument('-L', \
                        '--bam_list', \
                        required=True, \
                        help='Input list with bam file paths.')
    parser.add_argument('-j', \
                        '--job_uuid', \
                        required=True, \
                        help='Job uuid.')
    parser.add_argument('-f', \
                        '--reference', \
                        required=True, \
                        help='Reference path')
    parser.add_argument('-t', \
                        '--bed_file', \
                        required=True, \
                        help='BED file')
    parser.add_argument('-c', \
                        '--number_of_chunks', \
                        required=True, \
                        type=is_nat, \
                        default=30)
    parser.add_argument('-n', \
                        '--number_of_threads', \
                        required=True, \
                        type=is_nat, \
                        default=30)
    args = parser.parse_args()
    input_dict = {
        'job_uuid': args.job_uuid,
        'bam_list': args.bam_list,
        'ref': args.reference,
        'bed_file': args.bed_file
    }
    nchunks = args.number_of_chunks
    nthreads = args.number_of_threads
    cmds = list(freebayes_template(input_dict, nchunks))
    outputs = multi_commands(cmds, nthreads)
    # outputs = seq_commands(cmds)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'

if __name__ == '__main__':
    main()
