'''utilities for python runner'''

import subprocess
import logging
import os
import shutil
import hashlib
import json
import socket
import pkg_resources
import git

def pg_data_template():
    '''create postgres default dict'''
    git_path = os.path.dirname(os.path.realpath('__file__'))
    pg_data = {
        'job_uuid': None,
        'aliquot_id': None,
        'input_table': None,
        'project': None,
        'status': None,
        'datetime_start': None,
        'datetime_end': None,
        'download_time': 0.0,
        'bam_upload_time': 0.0,
        'gvcf_upload_time': 0.0,
        'bam_url': None,
        'gvcf_url': None,
        'bam_local_path': None,
        'gvcf_local_path': None,
        'bam_md5sum': None,
        'gvcf_md5sum': None,
        'bam_filesize': 0,
        'gvcf_filesize': 0,
        'harmonization_cwl_walltime': 0.0,
        'harmonization_cwl_cpu_percentage': 0.0,
        'haplotypecaller_cwl_walltime': 0.0,
        'haplotypecaller_cwl_cpu_percentage': 0.0,
        'whole_workflow_elapsed': 0.0,
        'hostname': socket.gethostname(),
        'cwl_version': pkg_resources.get_distribution("cwltool").version,
        'docker_version': 'Docker version 18.09.0, build 4d60db4',
        'cwl_input_json': None,
        'time_metrics_json': None,
        'git_hash': git.Repo(git_path, search_parent_directories=True).head.object.hexsha,
        'debug_path': None
    }
    return pg_data

def run_command(cmd, logger=None, shell_var=False):
    '''Runs a subprocess'''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode
    if logger is not None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)
        stderrdata = stderrdata.split("\n")
        for line in stderrdata:
            logger.info(line)
    return exit_code

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

def remove_dir(dirname):
    '''Remove a directory and all it's contents'''
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: {}".format(dirname))

def get_file_size(filename):
    ''' Gets file size '''
    fstats = os.stat(filename)
    return fstats.st_size

def get_md5(input_file):
    '''Estimates md5 of file '''
    blocksize = 65536
    hasher = hashlib.md5()
    with open(input_file, 'rb') as afile:
        buf = afile.read(blocksize)
        while buf:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()

def load_template_json():
    ''' load resource JSON file '''
    template_json_file = os.path.join(\
                         os.path.dirname(\
                         os.path.dirname(os.path.realpath('__file__'))),
                         "etc/template.json")
    dat = {}
    with open(template_json_file, 'r') as fhandle:
        dat = json.load(fhandle)
    return dat

def load_template_slurm():
    ''' load resource JSON file '''
    template_slurm_file = os.path.join(\
                         os.path.dirname(\
                         os.path.dirname(os.path.realpath('__file__'))),
                         "etc/template.sh")
    template_slurm_str = None
    with open(template_slurm_file, 'r') as fhandle:
        template_slurm_str = fhandle.read()
    return template_slurm_str

def targz_compress(logger, filename, dirname):
    '''Runs tar -cjvf'''
    cmd = ['tar', '-cjvf'] + [filename, dirname]
    exit_code = run_command(cmd, logger=logger)
    return exit_code
