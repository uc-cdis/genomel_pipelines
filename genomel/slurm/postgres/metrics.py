'''update postgres metrics'''

import postgres.mixins
import postgres.utils

class GenomelIndividualMetrics(postgres.mixins.IndMetricsTypeMixin, postgres.utils.Base):
    __tablename__ = 'genomel_individual_workflow_metrics'

def add_metrics(engine, table, data):
    """ add provided metrics to database """
    met = table(
        job_uuid=data['job_uuid'],
        slurm_jobid=data['slurm_jobid'],
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

class GenomelCohortGenotypingMetrics(postgres.mixins.CohMetricsTypeMixin, postgres.utils.Base):
    __tablename__ = 'genomel_cohort_genotyping_metrics'

def add_cohort_metrics(engine, table, data):
    """ add provided metrics to database """
    met = table(
        job_uuid=data['job_uuid'],
        slurm_jobid=data['slurm_jobid'],
        batch_id=data['batch_id'],
        input_table=data['input_table'],
        project=data['project'],
        runner_failures=data['runner_failures'],
        cromwell_status=data['cromwell_status'],
        cromwell_failures=data['cromwell_failures'],
        cromwell_finished_steps=data['cromwell_finished_steps'],
        cromwell_todo_steps=data['cromwell_todo_steps'],
        datetime_start=data['datetime_start'],
        datetime_end=data['datetime_end'],
        vcf_url=data['vcf_url'],
        vcf_local_path=data['vcf_local_path'],
        vcf_md5sum=data['vcf_md5sum'],
        vcf_filesize=data['vcf_filesize'],
        cwl_walltime=data['cwl_walltime'],
        cwl_cpu_percentage=data['cwl_cpu_percentage'],
        hostname=data['hostname'],
        cwl_version=data['cwl_version'],
        cromwell_version=data['cromwell_version'],
        docker_version=data['docker_version'],
        cwl_input_json=data['cwl_input_json'],
        time_metrics_json=data['time_metrics_json'],
        git_hash=data['git_hash'],
        debug_path=data['debug_path'])
    postgres.utils.create_table(engine, met)
    postgres.utils.add_metrics(engine, met)

class ProdMetrics(postgres.mixins.ProdMetricsTypeMixin, postgres.utils.Base):
    __tablename__ = 'pdc_freebayes_prod_metrics'

def add_pfp_metrics(engine, table, data):
    met = table(
        prod_time = data['prod_time'],
        nchunk_total = data['nchunk_total'],
        nchunk_passed = data['nchunk_passed'],
        nchunk_failed = data['nchunk_failed'],
        indiv_pass_time = data['indiv_pass_time'],
        indiv_fail_time = data['indiv_fail_time'],
        indiv_pass_mem = data['indiv_pass_mem'],
        indiv_fail_mem = data['indiv_fail_mem']
    )
    postgres.utils.create_table(engine, met)
    postgres.utils.add_metrics(engine, met)

