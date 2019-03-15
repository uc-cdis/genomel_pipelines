#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --workdir="/mnt/cephfs/cromwell_workdir"

basedir="/mnt/cephfs/cromwell_workdir"
project="{PROJECT}"
batch_id="{BATCH}"
job_uuid="{JOB_UUID}"
input_table="{INPUT_TABLE}"
psql_conf="/mnt/SCRATCH/reference/postgres_config"
gvcf_files_manifest="/mnt/cephfs/cromwell_workdir/gvcf_local_path.list"
gatk4_genotyping_thread_count="20"
number_of_chunks_for_gatk="100"
bam_files_manifest="/mnt/cephfs/cromwell_workdir/bam_local_path.list"
freebayes_thread_count="1"
number_of_chunks_for_freebayes="100"
upload_s3_bucket="s3://genomel/cohort_genotyping_output/"
cromwell_jar_path="/mnt/cephfs/cromwell_workdir/cromwell-38.jar"
repository="git@github.com:uc-cdis/genomel_pipelines.git"

cd $basedir

sudo git clone $repository genomel_pipelines
sudo chown ubuntu:ubuntu -R genomel_pipelines

/home/ubuntu/.virtualenvs/p2/bin/python \
$basedir/genomel_pipelines/genomel/slurm/genomel_cohort_genotyping_runner.py \
--basedir $basedir \
--project $project \
--batch_id $batch_id \
--job_uuid $job_uuid \
--input_table $input_table \
--psql_conf $psql_conf \
--gvcf_files_manifest $gvcf_files_manifest \
--gatk4_genotyping_thread_count $gatk4_genotyping_thread_count \
--number_of_chunks_for_gatk $number_of_chunks_for_gatk \
--bam_files_manifest $bam_files_manifest \
--freebayes_thread_count $freebayes_thread_count \
--number_of_chunks_for_freebayes $number_of_chunks_for_freebayes \
--upload_s3_bucket $upload_s3_bucket \
--cromwell_jar_path $cromwell_jar_path
