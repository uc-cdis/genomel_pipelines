#!/usr/bin/env python
'''Internal multithreading for GATK4.0.11 Cohort Genotyping, GenoMEL-PDC'''

import os
import sys
import argparse
import subprocess
import string
from functools import partial
from multiprocessing.dummy import Pool, Lock
import fnmatch
import vcf

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
            ipath = search_files(i.rstrip(), root_dir=search_dir)
            docker_path.append(ipath)
    with open('docker_path.list', 'w') as ohandle:
        for path in docker_path:
            ohandle.write('{}\n'.format(path))
    return os.path.abspath('docker_path.list')

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

def prepare_cmd(cmd_list):
    '''prepare cmd string template'''
    cmd_str = ' '.join(cmd_list)
    template = string.Template(cmd_str)
    return template

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

class GenomelGATK(object):
    '''this class describe the functions to run GenoMEL-PDC GATK4-0-11 Cohort Genotyping.'''
    def __init__(self, cmd_dict):
        self.job_uuid = cmd_dict['job_uuid']
        self.gvcf_list = cmd_dict['gvcf_list']
        self.ref = cmd_dict['ref']
        self.bed_file = cmd_dict['bed_file']
        self.nthreads = cmd_dict['nthreads']
        self.nchunks = cmd_dict['nchunks']
        self.importdb_output_dict = dict()
        self.search_dir = cmd_dict[cmd_dict['cwl_engine']]

    def cohort_genotyping(self):
        '''GATK4 GenotypeGVCFs executor'''
        cohort_cmd_list = self._prepare_genoytping_cmd()
        cmd_outputs = multi_commands(cohort_cmd_list, self.nthreads)
        if any(x != 0 for x in cmd_outputs):
            print 'Failed Genotyping'
            sys.exit(1)
        else:
            print 'Completed'

    def importdb(self):
        '''GATK4 GenomicsDBImport executor'''
        importdb_cmd_list = []
        region_list = []
        dbname_list = []
        for importdb_cmd, region, dbname in self._prepare_importdb_cmd():
            importdb_cmd_list.append(importdb_cmd)
            region_list.append(region)
            dbname_list.append(dbname)
        cmd_outputs = []
        for cmd in importdb_cmd_list:
            output = do_pool_commands(cmd)
            cmd_outputs.append(output)
        if any(x != 0 for x in cmd_outputs):
            print 'Failed importdb'
            sys.exit(1)
        else:
            for region, dbname in zip(region_list, dbname_list):
                self.importdb_output_dict[region] = dbname

    def _prepare_importdb_cmd(self):
        '''prepare importdb cmd'''
        cmd_list = [
            '/opt/gatk-4.0.11.0/gatk',
            '--java-options "-Xmx100g -Xms4g"',
            'GenomicsDBImport',
            '--sample-name-map', '${MAP}',
            '--genomicsdb-workspace-path', '${WORKSPACE}',
            '--batch-size', '200',
            '-L', '${REGION}',
            '--reader-threads', '${NTHREADS}'
        ]
        template = prepare_cmd(cmd_list)
        bed_region_list = self._prepare_region()
        for i, region in enumerate(bed_region_list):
            cmd = template.substitute(
                dict(
                    MAP=self._prepare_sample_path_map(),
                    WORKSPACE='genomicsdb-{}'.format(i),
                    REGION=region,
                    REF=self.ref,
                    NTHREADS=self.nthreads
                )
            )
            yield cmd, region, 'genomicsdb-{}'.format(i)

    def _prepare_sample_path_map(self):
        '''prepare sample-path map'''
        sample_map = dict()
        gvcf_path_list = []
        gvcf_docker_path = docker_path_list(self.gvcf_list, self.search_dir)
        with open(gvcf_docker_path, 'r') as fhandle:
            lines = fhandle.readlines()
            for path in lines:
                gvcf_path_list.append(path.rstrip())
        for gvcf in gvcf_path_list:
            sample_name = vcf.Reader(filename='{}'.format(gvcf)).samples[0]
            sample_map[sample_name] = gvcf
        with open('sample_path.map', 'w') as ohandle:
            for sample, path in sample_map.items():
                ohandle.write('{}\t{}\n'.format(sample, path))
        return os.path.abspath('sample_path.map')

    def _prepare_region(self):
        '''prepare N (N = nchunks) child region upon bed input'''
        bed_region = []
        with open(self.bed_file, 'r') as fhandle:
            lines = fhandle.readlines()
            nline = len(lines)/self.nchunks + 1
            child = [lines[i:i + nline] for i in xrange(0, len(lines), nline)]
            for chunk in child:
                get_region(chunk, bed_region)
        return bed_region

    def _prepare_genoytping_cmd(self):
        '''prepare cohort genotyping cmd'''
        cmd_list = [
            '/opt/gatk-4.0.11.0/gatk',
            '--java-options "-Xmx4g -Xms4g"',
            'GenotypeGVCFs',
            '-L', '${REGION}',
            '-R', '${REF}',
            '-O', '${OUTPUT}',
            '-V', '${WORKSPACE}',
            '-A', 'Coverage',
            '-A', 'QualByDepth',
            '-G', 'StandardAnnotation',
            '-new-qual'
        ]
        template = prepare_cmd(cmd_list)
        for region, dbname in self.importdb_output_dict.items():
            cmd = template.substitute(
                dict(
                    REGION=region,
                    REF=self.ref,
                    OUTPUT='{}.vcf.gz'.format(dbname),
                    WORKSPACE='gendb://{}'.format(dbname)
                )
            )
            yield cmd

def main():
    '''main'''
    parser = argparse.ArgumentParser('GenoMEL-PDC GATK4-0-11 Cohort Genotyping.')
    # Required flags.
    parser.add_argument('--gvcf_path', \
                        required=True, \
                        help='Input map with GVCFs file paths and their Sample name.')
    parser.add_argument('-j', \
                        '--job_uuid', \
                        required=True, \
                        help='Job uuid.')
    parser.add_argument('-f', \
                        '--reference', \
                        required=True, \
                        help='Reference path')
    parser.add_argument('-L', \
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
                        '--cwl_engine', \
                        required=True, \
                        choices=['cwltool', 'cromwell'], \
                        help='Choose CWL engine')

    args = parser.parse_args()
    input_dict = {
        'job_uuid': args.job_uuid,
        'gvcf_list': args.gvcf_path,
        'ref': args.reference,
        'bed_file': args.bed_file,
        'nthreads': args.number_of_threads,
        'nchunks': args.number_of_chunks,
        'cwl_engine': args.cwl_engine,
        'cwltool': '/var/',
        'cromwell': '/cromwell-executions/'
    }
    genomel_gatk = GenomelGATK(input_dict)
    genomel_gatk.importdb()
    genomel_gatk.cohort_genotyping()

if __name__ == '__main__':
    main()
