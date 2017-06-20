#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=XX_THREAD_COUNT_XX
#SBATCH --ntasks=1
#SBATCH --mem=XX_MEM_XX
#SBATCH --workdir="/mnt/SCRATCH/"

function cleanup (){
    echo "cleanup tmp data";
    sudo rm -rf $basedir;
}

java_heap="XX_MEM_XX"
read1_id="XX_READ1_XX"
read2_id="XX_READ2_XX"
project="XX_PROJECT_XX"
md5_r1="XX_MD5_R1_XX"
md5_r2="XX_MD5_R2_XX"
s3_url_r1="XX_S3URL_R1_XX"
s3_url_r2="XX_S3URL_R2_XX"
s3_profile="XX_S3PROFILE_XX"
s3_endpoint="XX_S3ENDPOINT_XX"
thread_count="XX_THREAD_COUNT_XX"
output_id="XX_OUTPUT_ID_XX"

basedir=`sudo mktemp -d genomel.algn.XXXXXXXXXX -p /mnt/SCRATCH/`
refdir="XX_REFDIR_XX"
s3dir="XX_S3DIR_XX"

repository="git@github.com:uc-cdis/cwl.git"
sudo chown ubuntu:ubuntu $basedir

cd $basedir

sudo git clone -b feat/slurm $repository genomel_cwl
sudo chown ubuntu:ubuntu -R genomel_cwl

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python genomel_cwl/slurm/genomel_alignment_pipeline.py \
--input_r1_id $read1_id \
--input_r2_id $read2_id \
--project $project \
--r1_md5 $md5_r1 \
--r2_md5 $md5_r2 \
--s3_url_r1 $s3_url_r1 \
--s3_url_r2 $s3_url_r2 \
--s3_profile $s3_profile \
--s3_endpoint $s3_endpoint \
--basedir $basedir \
--refdir $refdir \
--cwl $basedir/genomel_cwl/workflows/alignment_mark_duplicates.cwl.yaml \
--s3dir $s3dir \
--thread_count $thread_count \
--java_heap $java_heap \
--output_id $output_id