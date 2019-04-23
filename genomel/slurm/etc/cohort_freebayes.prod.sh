#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --workdir="/mnt/nfs/cromwell_workdir"

basedir="/mnt/nfs/cromwell_workdir"
project="{PROJECT}"
batch_id="{BATCH}"
job_uuid="{JOB_UUID}"
input_table="{INPUT_TABLE}"
psql_conf="/mnt/nfs/reference/postgres_config"
bed_files_manifest="/mnt/nfs/cromwell_workdir/bed_files.list"
freebayes_thread_count="15"
number_of_chunks_for_freebayes="160"
upload_s3_bucket="s3://genomel/cohort_genotyping_output/"
cromwell_jar_path="/mnt/nfs/cromwell_workdir/cromwell-36.jar"
repository="git@github.com:uc-cdis/genomel_pipelines.git"

cd $basedir

sudo git clone -b chore/setup $repository genomel_pipelines
sudo chown ubuntu:ubuntu -R genomel_pipelines

/home/ubuntu/.virtualenvs/p2/bin/python \
$basedir/genomel_pipelines/genomel/slurm/genomel_cohort_freebayes_runner.py \
--basedir $basedir \
--project $project \
--batch_id $batch_id \
--job_uuid $job_uuid \
--input_table $input_table \
--psql_conf $psql_conf \
--bed_files_manifest $bed_files_manifest \
--freebayes_thread_count $freebayes_thread_count \
--number_of_chunks_for_freebayes $number_of_chunks_for_freebayes \
--upload_s3_bucket $upload_s3_bucket \
--cromwell_jar_path $cromwell_jar_path
