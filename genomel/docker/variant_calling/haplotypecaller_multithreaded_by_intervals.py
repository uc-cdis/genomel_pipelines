#!/usr/bin/env python
'''Internal multithreading for Haplotypecaller on different chromosome regions'''

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

def get_region(intervals):
    '''get region from intervals'''
    interval_list = []
    with open(intervals, 'r') as fhandle:
        line = fhandle.readlines()
        for bed in line:
            blocks = bed.rstrip().rsplit('\t')
            intv = '{}:{}-{}'.format(blocks[0], int(blocks[1])+1, blocks[2])
            interval_list.append(intv)
    return interval_list

def cmd_template(cmd_dict):
    '''cmd template'''
    cmd_list = [
        'java', '-Xmx3G',
        '-jar', '/opt/GenomeAnalysisTK.jar',
        '-T', 'HaplotypeCaller',
        '-R', '${REF}',
        '-I', '${BAM}',
        '-L', '${INTERVAL}',
        '-D', '${SNP}',
        '-o', '${OUT}',
        '--emitRefConfidence', 'GVCF',
        '--variant_index_type', 'LINEAR',
        '--variant_index_parameter', '128000',
        '-minPruning', '3',
        '-stand_call_conf', '10',
        '-G', 'Standard',
        '-A', 'AlleleBalance',
        '-A', 'Coverage',
        '-A', 'HomopolymerRun',
        '-A', 'QualByDepth'
    ]
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for region in get_region(cmd_dict['interval']):
        interval_str = str(region).replace(':', '_').replace('-', '_')
        output = cmd_dict['job_uuid'] + '.' + interval_str + '.g.vcf.gz'
        cmd = template.substitute(
            dict(
                REF=cmd_dict['ref'],
                BAM=cmd_dict['bam'],
                INTERVAL=cmd_dict['interval'],
                SNP=cmd_dict['snp'],
                OUT=output
            )
        )
        yield cmd, output

def main():
    '''main'''
    parser = argparse.ArgumentParser('Internal multithreading GATK3 Haplotypecaller.')
    # Required flags.
    parser.add_argument('-b', \
                        '--bam', \
                        required=True, \
                        help='BAM file.')
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
                        default=30)
    args = parser.parse_args()
    input_dict = {
        'job_uuid': args.job_uuid,
        'bam': args.bam,
        'ref': args.reference,
        'interval': args.interval,
        'snp': args.snp
    }
    threads = args.thread_count
    hc_cmds = []
    hc_outs = []
    for i in list(cmd_template(input_dict)):
        hc_cmds.append(i[0])
        hc_outs.append(i[1])
    outputs = multi_commands(hc_cmds, threads)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'

if __name__ == '__main__':
    main()
