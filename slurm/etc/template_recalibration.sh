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

input_id="XX_INPUTID_XX"
project="XX_PROJECT_XX"
output_id="XX_OUTPUT_ID_XX"
md5="XX_MD5_XX"
s3_url="XX_S3URL_XX"
s3_profile="XX_S3PROFILE_XX"
s3_endpoint="XX_S3ENDPOINT_XX"
thread_count="XX_THREAD_COUNT_XX"

basedir=`sudo mktemp -d genomel.XXXXXXXXXX -p /mnt/SCRATCH/`
refdir="XX_REFDIR_XX"
s3dir="XX_S3DIR_XX"

repository="git@github.com:uc-cdis/cwl.git"
sudo chown ubuntu:ubuntu $basedir

cd $basedir

sudo git clone -b feat/slurm $repository genomel_cwl
sudo chown ubuntu:ubuntu -R genomel_cwl

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python genomel_cwl/slurm/genomel_recalibration_pipeline.py \
--input_id $input_id \
--output_id $output_id \
--project $project \
--md5 $md5 \
--s3_url $s3_url \
--s3_profile $s3_profile \
--s3_endpoint $s3_endpoint \
--basedir $basedir \
--refdir $refdir \
--cwl $basedir/genomel_cwl/workflows/recalibration-workflow.cwl.yaml \
--s3dir $s3dir \
--thread_count $thread_count
