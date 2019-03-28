#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --workdir="/mnt/glusterfs/genomel-cohort-cwl"

basedir="/mnt/glusterfs/genomel-cohort-cwl"
project="genomel_dev"
batch_id="gatk_01"
job_uuid="{JOB_UUID}"
input_table="{INPUT_TABLE}"
psql_conf="/mnt/SCRATCH/reference/postgres_config"
gvcf_files_manifest="/mnt/glusterfs/genomel-cohort-cwl/gvcf_local_path.list"
gatk4_genotyping_thread_count="20"
number_of_chunks_for_gatk="100"
upload_s3_bucket="s3://genomel/cohort_dev/cohort_gatk_output/"
cromwell_jar_path="/mnt/glusterfs/genomel-cohort-cwl/cromwell-36.jar"
repository="git@github.com:uc-cdis/genomel_pipelines.git"

cd $basedir

sudo git clone $repository genomel_pipelines
sudo chown ubuntu:ubuntu -R genomel_pipelines

/home/ubuntu/.virtualenvs/p2/bin/python \
$basedir/genomel_pipelines/genomel/slurm/genomel_cohort_gatk_runner.py \
--basedir $basedir \
--project $project \
--batch_id $batch_id \
--job_uuid $job_uuid \
--input_table $input_table \
--psql_conf $psql_conf \
--gvcf_files_manifest $gvcf_files_manifest \
--gatk4_genotyping_thread_count $gatk4_genotyping_thread_count \
--number_of_chunks_for_gatk $number_of_chunks_for_gatk \
--upload_s3_bucket $upload_s3_bucket \
--cromwell_jar_path $cromwell_jar_path
