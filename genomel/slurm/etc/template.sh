#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=30
#SBATCH --ntasks=1
#SBATCH --mem=100000
#SBATCH --workdir="/mnt/SCRATCH/"

function cleanup (){
    echo "cleanup tmp data";
    sudo rm -rf $basedir;
}

pipeline="{PIPELINE}"
aliquot_id="{ALIQUOT_ID}"
input_table="{INPUT_TABLE}"
project="{PROJECT}"
download_s3_profile="{D_S3_PROFILE}"
download_s3_endpoint="{D_S3_ENDPOINT}"
{PIPELINE_VARIABLES}

basedir=`sudo mktemp -d {PIPELINE}.XXXXXXXXXX -p /mnt/SCRATCH/`

repository="git@github.com:uc-cdis/genomel_pipelines.git"
sudo chown ubuntu:ubuntu $basedir

cd $basedir

sudo git clone $repository genomel_pipelines
sudo chown ubuntu:ubuntu -R genomel_pipelines

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python \
$basedir/genomel_pipelines/genomel/slurm/genomel_individual_aliquot_runner.py \
$pipeline \
--basedir $basedir \
--cwlwf $basedir/genomel_pipelines/genomel/cwl/genomel_individual_workflow.cwl \
--aliquot_id $aliquot_id \
--input_table $input_table \
--project $project \
--download_s3_profile $download_s3_profile \
--download_s3_endpoint $download_s3_endpoint \
{PIPELINE_CMD}
