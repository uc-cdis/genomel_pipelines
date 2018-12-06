#!/usr/bin/env python
'''Internal multithreading for Freebayes, GenoMEL-PDC'''

import os
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

def get_region(intervals, nthreads):
    '''prepare N (N = nthreads) child bed files upon bed input'''
    bed_path = []
    with open(intervals, 'r') as fhandle:
        lines = fhandle.readlines()
        nline = len(lines)/nthreads + 1
        child = [lines[i:i + nline] for i in xrange(0, len(lines), nline)]
        for i, olines in enumerate(child):
            with open('{}.bed'.format(i), 'w') as ohandle:
                for line in olines:
                    ohandle.write('{}'.format(line))
            bed_path.append(os.path.abspath('{}.bed'.format(i)))
    return bed_path

def freebayes_template(cmd_dict, nthreads):
    '''cmd template'''
    cmd_list = [
        '/opt/freebayes/bin/freebayes',
        '-L', '${BAM_LIST}',
        '-f', '${REF}',
        '-t', '${BED}',
        '-v', '${OUTPUT}',
        '--use-best-n-alleles', '6'
    ]
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for bed_file in get_region(cmd_dict['bed_file'], nthreads):
        bed_prefix = os.path.basename(bed_file).split('.')[0]
        output = cmd_dict['job_uuid'] + '.' + bed_prefix + '.vcf'
        cmd = template.substitute(
            dict(
                BAM_LIST=cmd_dict['bam_list'],
                REF=cmd_dict['ref'],
                BED=bed_file,
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
                        '--thread_count', \
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
    nthreads = args.thread_count
    cmds = list(freebayes_template(input_dict, nthreads))
    outputs = multi_commands(cmds, nthreads)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'

if __name__ == '__main__':
    main()
