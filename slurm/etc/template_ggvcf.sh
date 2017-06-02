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

input_list="XX_INPUTLIST_XX"
output_id="XX_OUTPUT_ID_XX"
project="XX_PROJECT_XX"
s3_profile="XX_S3PROFILE_XX"
s3_endpoint="XX_S3ENDPOINT_XX"

thread_count="XX_THREAD_COUNT_XX"
java_heap="XX_JAVAHEAP_XX"

basedir=`sudo mktemp -d genomel.ggvcf.XXXXXXXXXX -p /mnt/SCRATCH/`
refdir="XX_REFDIR_XX"
s3dir="XX_S3DIR_XX"
intervals="XX_INTERVALS_XX"
chunk="XX_BLOCK_XX"

repository="git@github.com:uc-cdis/cwl.git"
sudo chown ubuntu:ubuntu $basedir

cd $basedir

sudo git clone -b feat/slurm $repository genomel_cwl
sudo chown ubuntu:ubuntu -R genomel_cwl

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python genomel_cwl/slurm/genomel_ggvcf_pipeline.py \
--input_list $input_list \
--output_id $output_id \
--project $project \
--s3_profile $s3_profile \
--s3_endpoint $s3_endpoint \
--basedir $basedir \
--refdir $refdir \
--cwl $basedir/genomel_cwl/tools/variant_detection/haplotypecaller/GenotypeGVCFs.cwl.yaml \
--s3dir $s3dir \
--thread_count $thread_count \
--java_heap $java_heap \
--chunk $chunk \
--intervals $intervals
