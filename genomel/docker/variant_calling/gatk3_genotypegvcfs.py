#!/usr/bin/env python
'''Internal multithreading for GATK3 GenotypeGVCFs'''

import os
import sys
import argparse
import subprocess
import string
from itertools import groupby
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

def get_region(intervals):
    '''get region from intervals'''
    interval_path = []
    with open(intervals, 'r') as fhandle:
        lines = fhandle.readlines()
        for chro, region in groupby(lines, lambda x: x.rstrip().rsplit('\t')[0]):
            chr_bed = '{}.bed'.format(chro)
            with open(chr_bed, 'w') as ohandle:
                for line in region:
                    ohandle.write('{}'.format(line))
            interval_path.append(os.path.abspath(chr_bed))
    return interval_path

def genotypegvcfs_template(cmd_dict):
    '''cmd template'''
    cmd_list = [
        'java', '-Xmx3G',
        '-jar', '/opt/GenomeAnalysisTK.jar',
        '-T', 'GenotypeGVCFs',
        '-R', '${REF}',
        '-L', '${INTERVAL}',
        '-D', '${SNP}',
        '-o', '${OUT}',
        '-A', 'AlleleBalance',
        '-A', 'Coverage',
        '-A', 'HomopolymerRun',
        '-A', 'QualByDepth'
    ]
    for gvcf in cmd_dict['gvcf']:
        cmd_list.extend(['-V', gvcf])
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for region in get_region(cmd_dict['interval']):
        interval_str = os.path.basename(region).split('.')[0]
        output = cmd_dict['job_uuid'] + '.' + interval_str + '.vcf.gz'
        cmd = template.substitute(
            dict(
                REF=cmd_dict['ref'],
                INTERVAL=region,
                SNP=cmd_dict['snp'],
                OUT=output
            )
        )
        yield cmd

def main():
    '''main'''
    parser = argparse.ArgumentParser('GATK3 GenoMEL GenotypeGVCFs.')
    # Required flags.
    parser.add_argument('-v', \
                        '--gvcf', \
                        required=True, \
                        nargs='+', \
                        help='GVCF file.')
    parser.add_argument('-j', \
                        '--job_uuid', \
                        required=True, \
                        help='Job uuid.')
    parser.add_argument('-r', \
                        '--reference', \
                        required=True, \
                        help='Reference path')
    parser.add_argument('-i', \
                        '--interval', \
                        required=True, \
                        help='Interval files')
    parser.add_argument('-s', \
                        '--snp', \
                        required=True, \
                        help='Reference SNP file path')
    parser.add_argument('-c', \
                        '--thread_count', \
                        required=True, \
                        type=is_nat, \
                        default=25)
    args = parser.parse_args()
    input_dict = {
        'job_uuid': args.job_uuid,
        'gvcf': args.gvcf,
        'ref': args.reference,
        'interval': args.interval,
        'snp': args.snp
    }
    threads = args.thread_count
    cmds = list(genotypegvcfs_template(input_dict))
    outputs = multi_commands(cmds, threads)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'

if __name__ == '__main__':
    main()
