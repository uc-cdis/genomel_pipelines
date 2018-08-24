import os
import sys
import subprocess

import utils.pipeline

def aws_s3_get(logger, remote_input, local_output, profile, endpoint_url, recursive=True):
    '''
    Uses aws cli to get files from s3.
    remote_input s3bin for files
    local_output path to location of output files
    profile aws s3 credential profile
    endpoint_url endpoint url for s3 store
    '''
    if (remote_input != ""):
        cmd = ['/home/ubuntu/.virtualenvs/p2/bin/aws', '--profile', profile,
               '--endpoint-url', endpoint_url, '--no-verify-ssl', 's3', 'cp', remote_input,
               local_output]
        if recursive: cmd.append('--recursive')
        exit_code = utils.pipeline.run_command(cmd, logger)

    else:
        raise Exception("invalid input %s" % remote_input)

    return exit_code

def aws_s3_put(logger, remote_output, local_input, profile, endpoint_url, recursive=True):
    '''
    Uses aws cli to put files into s3.
    local_input path to files you want to upload
    remote_output s3bin for uploading files
    profile aws s3 credential profile
    endpoint_url endpoint url for s3 store
    '''
    if (remote_output != "" and (os.path.isfile(local_input) or os.path.isdir(local_input))):
        cmd = ['/home/ubuntu/.virtualenvs/p2/bin/aws', '--profile', profile,
               '--endpoint-url', endpoint_url, '--no-verify-ssl', 's3', 'cp', local_input,
               remote_output]
        if recursive: cmd.append('--recursive')
        exit_code = utils.pipeline.run_command(cmd, logger)

    else:
        raise Exception("invalid input %s or output %s" %(local_input, remote_output))
    return exit_code
