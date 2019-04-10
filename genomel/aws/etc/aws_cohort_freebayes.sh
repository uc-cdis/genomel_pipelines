#!/bin/bash

basedir="/data2/cromwell_workdir"
project="genomel_prod"
batch_id="aws_freebayes_01"
job_uuid="13189d29-db47-4830-a895-f2b907a39167"
freebayes_thread_count="64"
number_of_chunks_for_freebayes="1280"
upload_s3_bucket="s3://genomel/cohort_genotyping_output/"
cromwell_jar_path="/data2/cromwell_workdir/cromwell-36.jar"
repository="git@github.com:uc-cdis/genomel_pipelines.git"

cd $basedir

/home/ubuntu/.virtualenvs/p2/bin/python \
$basedir/genomel_pipelines/genomel/aws/aws_cohort_freebayes_runner.py \
--basedir $basedir \
--project $project \
--batch_id $batch_id \
--job_uuid $job_uuid \
--freebayes_thread_count $freebayes_thread_count \
--number_of_chunks_for_freebayes $number_of_chunks_for_freebayes \
--upload_s3_bucket $upload_s3_bucket \
--cromwell_jar_path $cromwell_jar_path
