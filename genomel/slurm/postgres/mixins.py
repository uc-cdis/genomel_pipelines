'''
Postgres mixins
'''
from sqlalchemy import Column, Integer, String, Float, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY

class IndMetricsTypeMixin(object):
    ''' Gather timing metrics with input uuids '''
    id = Column(Integer, primary_key=True)
    job_uuid = Column(String)
    slurm_jobid = Column(Integer)
    aliquot_id = Column(String)
    input_table = Column(String)
    project = Column(String)
    status = Column(String)
    datetime_start = Column(String)
    datetime_end = Column(String)
    download_time = Column(Float)
    bam_upload_time = Column(Float)
    gvcf_upload_time = Column(Float)
    bam_url = Column(String)
    gvcf_url = Column(String)
    bam_local_path = Column(String)
    gvcf_local_path = Column(String)
    bam_md5sum = Column(String)
    gvcf_md5sum = Column(String)
    bam_filesize = Column(BigInteger)
    gvcf_filesize = Column(BigInteger)
    alignment_cwl_walltime = Column(Float)
    alignment_cwl_cpu_percentage = Column(String)
    harmonization_cwl_walltime = Column(Float)
    harmonization_cwl_cpu_percentage = Column(String)
    haplotypecaller_cwl_walltime = Column(Float)
    haplotypecaller_cwl_cpu_percentage = Column(String)
    whole_workflow_elapsed = Column(Float)
    hostname = Column(String)
    cwl_version = Column(String)
    docker_version = Column(String)
    cwl_input_json = Column(String)
    time_metrics_json = Column(String)
    git_hash = Column(String)
    debug_path = Column(String)

    def __repr__(self):
        return "<IndMetricsTypeMixin(job_uuid={}, whole_workflow_elapsed={}, status={})>".format(
            self.job_uuid, self.whole_workflow_elapsed, self.status
        )

class CohMetricsTypeMixin(object):
    ''' Gather timing metrics with input uuids '''
    id = Column(Integer, primary_key=True)
    job_uuid = Column(String)
    slurm_jobid = Column(Integer)
    batch_id = Column(String)
    input_table = Column(String)
    project = Column(String)
    runner_failures = Column(String)
    cromwell_status = Column(String)
    cromwell_failures = Column(String)
    cromwell_finished_steps = Column(ARRAY(String))
    cromwell_todo_steps = Column(ARRAY(String))
    datetime_start = Column(String)
    datetime_end = Column(String)
    vcf_url = Column(ARRAY(String))
    vcf_local_path = Column(ARRAY(String))
    vcf_md5sum = Column(ARRAY(String))
    vcf_filesize = Column(ARRAY(BigInteger))
    cwl_walltime = Column(Float)
    cwl_cpu_percentage = Column(String)
    hostname = Column(String)
    cwl_version = Column(String)
    cromwell_version = Column(String)
    docker_version = Column(String)
    cwl_input_json = Column(String)
    time_metrics_json = Column(String)
    git_hash = Column(String)
    debug_path = Column(String)
    def __repr__(self):
        return "<CohMetricsTypeMixin(job_uuid={}, cwl_walltime={}, status={})>".format(
            self.job_uuid, self.cwl_walltime, self.status
        )

class ProdMetricsTypeMixin(object):
    id = Column(Integer, primary_key=True)
    prod_time = Column(Float)
    nchunk_total = Column(Integer)
    nchunk_passed = Column(Integer)
    nchunk_failed = Column(Integer)
    indiv_pass_time = Column(ARRAY(Float))
    indiv_fail_time = Column(ARRAY(Float))
    indiv_pass_mem = Column(ARRAY(Float))
    indiv_fail_mem = Column(ARRAY(Float))
    def __repr__(self):
        return "<ProdMetricsTypeMixin(prod_time={}, nchunk_total={}, nchunk_passed={}, nchunk_failed={})>".format(
            self.prod_time, self.nchunk_total, self.nchunk_passed, self.nchunk_failed
        )
