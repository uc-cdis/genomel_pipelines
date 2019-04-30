#!/usr/bin/env python
'''Internal multithreading for Freebayes, GenoMEL-PDC'''

import os
import sys
import argparse
import subprocess
import string
from functools import partial
from multiprocessing.dummy import Pool, Lock
import logging
import json

def is_nat(pos):
    '''Checks that a value is a natural number.'''
    if int(pos) > 0:
        return int(pos)
    raise argparse.ArgumentTypeError('{} must be positive, non-zero'.format(pos))

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

def freebayes_template(cmd_dict, dct, nchunks):
    '''cmd template'''
    cmd_list = [
        '/usr/bin/time', '-v',
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
        dct[bed_file] = dict()
        dct[bed_file]['vcf'] = os.path.abspath(output)
        yield cmd

def parse_bed_from_cmd(cmd):
    cmd_list = cmd.split(' ')
    bed = cmd_list[8]
    return bed

def parse_stderr(s, cdct):
    """Parse timing information from GNU time.
    """
    for line in s.decode().format().split('\n'):
        line = line.strip()
        if line.startswith('User time (seconds):'):
            user_time = float(line.split(':')[1].strip())
        if line.startswith('System time (seconds):'):
            system_time = float(line.split(':')[1].strip())
        if line.startswith('Percent of CPU this job got:'):
            percent_of_cpu = int(line.split(':')[1].strip().rstrip('%'))
        if line.startswith('Elapsed (wall clock) time (h:mm:ss or m:ss):'):
            value = line.replace('Elapsed (wall clock) time (h:mm:ss or m:ss):', '').strip()
            #hour case
            if value.count(':') == 2:
                hours = int(value.split(':')[0])
                minutes = int(value.split(':')[1])
                seconds = float(value.split(':')[2])
                total_seconds = (hours * 60 * 60) + (minutes * 60) + seconds
                wall_clock = total_seconds
            if value.count(':') == 1:
                minutes = int(value.split(':')[0])
                seconds = float(value.split(':')[1])
                total_seconds = (minutes * 60) + seconds
                wall_clock = total_seconds
        if line.startswith('Maximum resident set size (kbytes):'):
            maximum_resident_set_size = int(line.split(':')[1].strip())
        if line.startswith('Exit status:'):
            exit_status = int(line.split(':')[1].strip())
        cdct['user_time'] = user_time
        cdct['system_time'] = system_time
        cdct['percent_of_cpu'] = percent_of_cpu
        cdct['wall_clock'] = wall_clock
        cdct['maximum_resident_set_size'] = maximum_resident_set_size
        cdct['exit_status'] = exit_status
    return cdct

def do_pool_commands(cmd, logger, dct, lock = Lock()):
    try:
        output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_stdout, output_stderr = output.communicate()
        with lock:
            logger.info('running: %s', cmd)
            logger.info(output_stdout)
            bed = parse_bed_from_cmd(cmd)
            child_dict = parse_stderr(output_stderr, dct[bed])
            logger.info('processed_bed: %s', bed)
            logger.info('output_vcf: %s', child_dict['vcf'])
            logger.info('system_time: %s', child_dict['system_time'])
            logger.info('user_time: %s', child_dict['user_time'])
            logger.info('wall_clock: %s', child_dict['wall_clock'])
            logger.info('percent_of_cpu: %s', child_dict['percent_of_cpu'])
            logger.info('maximum_resident_set_size: %s', child_dict['maximum_resident_set_size'])
            logger.info('exit_status: %s', child_dict['exit_status'])
            if child_dict['exit_status'] == 0:
                os.rename(bed, os.path.join('pass', os.path.basename(bed)))
                os.rename(child_dict['vcf'], os.path.join('pass', os.path.basename(child_dict['vcf'])))
    except BaseException, e:
        logger.error('Failed: %s', e)

def multi_commands(cmds, thread_count, dct, logger):
    pool = Pool(int(thread_count))
    pool.map(partial(do_pool_commands, dct, logger=logger), cmds)

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
    log_file = '{}.pdc_freebayes_docker.log'.format(input_dict['job_uuid'])
    logger = setup_logging(
        logging.INFO,
        'pdc_freebayes',
        log_file
    )
    os.mkdir('pass')
    job_dict = dict()
    cmds = list(freebayes_template(input_dict, job_dict, nchunks))
    multi_commands(cmds, nthreads, job_dict, logger)
    with open('pass/metrics.json', 'wt') as ohandle:
        json.dump(job_dict, ohandle, indent=4)

if __name__ == '__main__':
    main()