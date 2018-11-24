'''update postgres metrics'''

import postgres.mixins
import postgres.utils

class GenomelIndividualMetrics(postgres.mixins.IndMetricsTypeMixin, postgres.utils.Base):
    __tablename__ = 'genomel_individual_workflow_metrics'

def add_metrics(engine, table, data):
    """ add provided metrics to database """
    met = table(
        job_uuid=data['job_uuid'],
        aliquot_id=data['aliquot_id'],
        input_table=data['input_table'],
        project=data['project'],
        status=data['status'],
        datetime_start=data['datetime_start'],
        datetime_end=data['datetime_end'],
        download_time=data['download_time'],
        bam_upload_time=data['bam_upload_time'],
        gvcf_upload_time=data['gvcf_upload_time'],
        bam_url=data['bam_url'],
        gvcf_url=data['gvcf_url'],
        bam_local_path=data['bam_local_path'],
        gvcf_local_path=data['gvcf_local_path'],
        bam_md5sum=data['bam_md5sum'],
        gvcf_md5sum=data['gvcf_md5sum'],
        bam_filesize=data['bam_filesize'],
        gvcf_filesize=data['gvcf_filesize'],
        alignment_cwl_walltime=data['alignment_cwl_walltime'],
        alignment_cwl_cpu_percentage=data['alignment_cwl_cpu_percentage'],
        harmonization_cwl_walltime=data['harmonization_cwl_walltime'],
        harmonization_cwl_cpu_percentage=data['harmonization_cwl_cpu_percentage'],
        haplotypecaller_cwl_walltime=data['haplotypecaller_cwl_walltime'],
        haplotypecaller_cwl_cpu_percentage=data['haplotypecaller_cwl_cpu_percentage'],
        whole_workflow_elapsed=data['whole_workflow_elapsed'],
        hostname=data['hostname'],
        cwl_version=data['cwl_version'],
        docker_version=data['docker_version'],
        cwl_input_json=data['cwl_input_json'],
        time_metrics_json=data['time_metrics_json'],
        git_hash=data['git_hash'],
        debug_path=data['debug_path'])
    postgres.utils.create_table(engine, met)
    postgres.utils.add_metrics(engine, met)
