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

def cohort_data_template():
    '''create postgres default dict'''
    git_path = os.path.dirname(os.path.realpath(__file__))
    cohort_data = {
        'job_uuid': None,
        'batch_id': None,
        'project': None,
        'runner_failures': None,
        'cromwell_status': None,
        'cromwell_failures': None,
        'cromwell_finished_steps': None,
        'cromwell_todo_steps': None,
        'datetime_start': None,
        'datetime_end': None,
        'vcf_url': None,
        'vcf_local_path': None,
        'vcf_md5sum': None,
        'vcf_filesize': None,
        'cwl_walltime': None,
        'cwl_cpu_percentage': None,
        'hostname': socket.gethostname(),
        'cwl_version': pkg_resources.get_distribution("cwltool").version,
        'cromwell_version': None,
        'docker_version': 'Docker version 18.09.3, build 774a1f4',
        'cwl_input_json': None,
        'time_metrics_json': None,
        'git_hash': git.Repo(git_path, search_parent_directories=True).head.object.hexsha,
        'debug_path': None
    }
    return cohort_data

def create_cwl_array_input(manifest):
    '''create cwl array type input json'''
    path_list = []
    with open(manifest, 'r') as fhandle:
        files = fhandle.readlines()
        for fpath in files:
            path = {"class": "File", "path": fpath.rstrip()}
            path_list.append(path)
    return path_list

def run_command(cmd, logger=None, output=None, shell_var=False):
    '''Runs a subprocess'''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                             shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode
    if logger:
        logger.info(cmd)
        if output:
            with open(output, 'wt') as ohandle:
                ohandle.write(stdoutdata)
        else:
            for line in stdoutdata.split("\n"):
                logger.info(line)
        for line in stderrdata.split("\n"):
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

def move_file(cur_file, new_dir):
    '''move file'''
    if os.path.isdir(new_dir):
        new_file = os.path.join(new_dir, os.path.basename(cur_file))
        shutil.move(cur_file, new_file)
    else:
        raise Exception("Invalid directory: {}".format(new_dir))

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

def load_json(fpath):
    '''load json'''
    dic = {}
    with open(fpath, 'rt') as fhandle:
        dic = json.load(fhandle)
    return dic

def targz_compress(logger, filename, dirname):
    '''Runs tar -cjvf'''
    cmd = ['tar', '-cjvf'] + [filename, dirname]
    exit_code = run_command(cmd, logger)
    return exit_code

def aws_s3_put(logger, remote_output, local_input, profile, endpoint_url, recursive=True):
    '''Uses local aws cli to put files into s3'''
    if (remote_output != "" and (os.path.isfile(local_input) or os.path.isdir(local_input))):
        cmd = ['/home/ubuntu/.virtualenvs/p2/bin/aws', '--profile', profile,
               '--endpoint-url', endpoint_url, 's3', 'cp', local_input,
               remote_output, '--no-verify-ssl']
        if recursive:
            cmd.append('--recursive')
        exit_code = run_command(cmd, logger)
    else:
        raise Exception("invalid input %s or output %s" %(local_input, remote_output))
    return exit_code
