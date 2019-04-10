#!/usr/bin/env python
'''Internal multithreading for Freebayes, GenoMEL-PDC'''

import os
import sys
import argparse
import subprocess
import string
from functools import partial
from multiprocessing.dummy import Pool, Lock
import fnmatch
import logging

def setup_logging(level, log_name, log_filename):
    '''Sets up a logger'''
    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    if log_filename is None:
        stream_handler = logging.StreamHandler()
    else:
        stream_handler = logging.FileHandler(log_filename, mode='w')
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(stream_handler)
    return logger

def is_nat(pos):
    '''Checks that a value is a natural number.'''
    if int(pos) > 0:
        return int(pos)
    raise argparse.ArgumentTypeError('{} must be positive, non-zero'.format(pos))

def do_pool_commands(cmd, logger, lock = Lock()):
    try:
        output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_stdout, output_stderr = output.communicate()
        with lock:
            logger.info('running: %s', cmd)
            logger.info(output_stdout)
            logger.info(output_stderr)
            logger.info('exitcode: %s', output.wait())
    except BaseException, e:
        logger.error('Failed: %s', e)
    return output.wait()
        
def multi_commands(cmds, thread_count, logger):
    pool = Pool(int(thread_count))
    outputs = pool.map(partial(do_pool_commands, logger=logger), cmds)
    return outputs

def get_region(intervals, nchunks):
    '''prepare N (N = nchunks) child bed files upon bed input'''
    bed_path = []
    with open(intervals, 'r') as fhandle:
        lines = fhandle.readlines()
        nline = len(lines)/nchunks + 1
        child = [lines[i:i + nline] for i in xrange(0, len(lines), nline)]
        for i, olines in enumerate(child):
            with open('{}.bed'.format(i), 'w') as ohandle:
                for line in olines:
                    ohandle.write('{}'.format(line))
            bed_path.append(os.path.abspath('{}.bed'.format(i)))
    return bed_path

def freebayes_template(cmd_dict, nchunks):
    '''cmd template'''
    cmd_list = [
        '/opt/freebayes/bin/freebayes',
        '-b', '${BAM}',
        '-f', '${REF}',
        '-t', '${BED}',
        '-v', '${OUTPUT}',
        '--use-best-n-alleles', '4'
    ]
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for i, bed_file in enumerate(get_region(cmd_dict['bed_file'], nchunks)):
        output = cmd_dict['job_uuid'] + '.' + str(i) + '.vcf'
        cmd = template.substitute(
            dict(
                BAM=cmd_dict['bam'],
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
    parser.add_argument('-b', \
                        '--bam', \
                        required=True, \
                        help='Input merged bam file path.')
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
        'bam': args.bam,
        'ref': args.reference,
        'bed_file': args.bed_file
    }
    nchunks = args.number_of_chunks
    nthreads = args.number_of_threads
    log_file = 'aws_freebayes_docker.log'
    logger = setup_logging(
        logging.INFO,
        'aws_freebayes',
        log_file
    )
    cmds = list(freebayes_template(input_dict, nchunks))
    outputs = multi_commands(cmds, nthreads, logger)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'

if __name__ == '__main__':
    main()
