#!/usr/bin/env python
'''Internal multithreading for Novoalign-dedup on multiple readgroups'''

from __future__ import division
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

def get_chunksize(total_number_of_rg, threads):
    '''get chunksize for pool.map()'''
    chunksize = float(int(total_number_of_rg)*int(threads)/32)
    if chunksize % 1 > 0:
        chunksize = int(chunksize) + 1
    else:
        chunksize = int(chunksize)
    return chunksize

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

def multi_commands(cmds, thread_count, chunksize, shell_var=True):
    '''run commands on number of threads'''
    pool = Pool(int(thread_count))
    output = pool.map(partial(do_pool_commands, shell_var=shell_var), cmds, chunksize)
    return output

def cmd_template(threads, dbname, cmd_pair):
    '''cmd template'''
    cmd_list = [
        '/opt/novocraft/novoalign',
        '-c', '${NTHREADS}',
        '-d', '${DBNAME}',
        '-f', '${READ1}', '${READ2}',
        '-F', 'STDFQ',
        '-i', 'PE',
        '300,125',
        '-o', 'SAM',
        '"${READGROUP_LINE}"',
        '|', '/opt/samblaster-v.0.1.24/samblaster', '-i', '/dev/stdin', '-o', '/dev/stdout',
        '|', '/opt/sambamba-0.6.8-linux-static', 'view', '-t',
        '${NTHREADS}', '-f', 'bam', '-l', '0', '-S', '/dev/stdin'
        '|', '/opt/sambamba-0.6.8-linux-static', 'sort', '-t', '${NTHREADS}',
        '--natural-sort', '-m', '15GiB', '--tmpdir', './',
        '-o', '${READGROUP_NAME}.unsorted.bam', '-l', '5', '/dev/stdin'
    ]
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for read1, read2, rgl, rgn in cmd_pair:
        cmd = template.substitute(
            dict(
                NTHREADS=threads,
                DBNAME=dbname,
                READ1=read1,
                READ2=read2,
                READGROUP_LINE=rgl,
                READGROUP_NAME=rgn
            )
        )
        yield cmd

def main():
    '''main'''
    parser = argparse.ArgumentParser('Internal Novoalign-dedup on multiple readgroups.')
    # Required flags.
    parser.add_argument('-f1', \
                        '--fastq_read1', \
                        required=True, \
                        nargs='+', \
                        help='Fastq read 1.')
    parser.add_argument('-f2', \
                        '--fastq_read2', \
                        required=True, \
                        nargs='+', \
                        help='Fastq read 2.')
    parser.add_argument('-g', \
                        '--readgroup_lines', \
                        required=True, \
                        nargs='+', \
                        help='Read group lines from BAM header')
    parser.add_argument('-n', \
                        '--readgroup_names', \
                        required=True, \
                        nargs='+', \
                        help='Read group ids from BAM header')
    parser.add_argument('-d', \
                        '--dbfile_for_novoalign', \
                        required=True, \
                        help='Reference path')
    parser.add_argument('-t', \
                        '--thread_count', \
                        required=True, \
                        type=is_nat, \
                        default=8)
    args = parser.parse_args()

    if len(args.fastq_read1) == len(args.fastq_read2) \
        == len(args.readgroup_lines) == len(args.readgroup_names):
        input_pair = zip(args.fastq_read1, args.fastq_read2, \
                         args.readgroup_lines, args.readgroup_names)
    else:
        print 'Readgroups count does not match fastqs.'
        sys.exit(1)
    threads = args.thread_count
    dbname = args.dbfile_for_novoalign
    chunksize = get_chunksize(len(args.readgroup_names), threads)
    novo_cmd = list(cmd_template(threads, dbname, input_pair))
    print 'Running {} readgroup alignment(s). {} thread(s) for each in total {} round(s)'\
          .format(len(args.readgroup_names), threads, chunksize)
    outputs = multi_commands(novo_cmd, threads, chunksize)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed {} readgroup alignment(s). {} thread(s) for each in total {} round(s)'\
              .format(len(args.readgroup_names), threads, chunksize)

if __name__ == '__main__':
    main()
