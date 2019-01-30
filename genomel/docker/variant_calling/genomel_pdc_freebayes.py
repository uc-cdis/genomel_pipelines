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

def search_files(file_search_str, root_dir=os.getcwd(), abs_path=True, recurse=True):
    '''search files'''
    matches = []
    if recurse:
        for root, dirnames, filenames in os.walk(root_dir):
            for filename in fnmatch.filter(filenames, file_search_str):
                if abs_path:
                    matches.append(os.path.join(root, filename))
                else:
                    matches.append(filename)
    else:
        matches = fnmatch.filter(os.listdir(), file_search_str)
    if len(matches) == 1:
        return matches[0]
    return sorted(matches)

def docker_path_list(file_basename_list, search_dir):
    '''create docker path list'''
    docker_path = []
    with open(file_basename_list, 'r') as fhandle:
        basename = fhandle.readlines()
        for i in basename:
            ipath = search_files(
                os.path.basename(i.rstrip()),
                root_dir=search_dir
            )
            docker_path.append(ipath)
    with open('docker_path.list', 'w') as ohandle:
        for path in docker_path:
            ohandle.write('{}\n'.format(path))
    return os.path.abspath('docker_path.list')

def get_bam_path_list(bam_list, cromwell=False):
    '''get bam files path'''
    if not cromwell:
        return bam_list
    search_dir = '/cromwell-executions/'
    new_bam_list = docker_path_list(bam_list, search_dir)
    return new_bam_list

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
        '-L', '${BAM_LIST}',
        '-f', '${REF}',
        '-t', '${BED}',
        '-v', '${OUTPUT}',
        '--use-best-n-alleles', '6'
    ]
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    for i, bed_file in enumerate(get_region(cmd_dict['bed_file'], nchunks)):
        output = cmd_dict['job_uuid'] + '.' + str(i) + '.vcf'
        cmd = template.substitute(
            dict(
                BAM_LIST=get_bam_path_list(cmd_dict['bam_list'], cromwell=cmd_dict['cromwell']),
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
                        '--number_of_chunks', \
                        required=True, \
                        type=is_nat, \
                        default=30)
    parser.add_argument('-n', \
                        '--number_of_threads', \
                        required=True, \
                        type=is_nat, \
                        default=30)
    parser.add_argument('-e', \
                        '--cromwell_engine', \
                        action="store_true", \
                        help='If specified, it will search files in docker env.')

    args = parser.parse_args()
    input_dict = {
        'job_uuid': args.job_uuid,
        'bam_list': args.bam_list,
        'ref': args.reference,
        'bed_file': args.bed_file,
        'cromwell': args.cromwell_engine
    }
    nchunks = args.number_of_chunks
    nthreads = args.number_of_threads
    cmds = list(freebayes_template(input_dict, nchunks))
    outputs = multi_commands(cmds, nthreads)
    if any(x != 0 for x in outputs):
        print 'Failed'
        sys.exit(1)
    else:
        print 'Completed'

if __name__ == '__main__':
    main()
