'''
Postgres mixins
'''
from sqlalchemy import Column, Integer, String, Float

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
    bam_filesize = Column(Integer)
    gvcf_filesize = Column(Integer)
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
