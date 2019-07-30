#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=5
#SBATCH --ntasks=1
#SBATCH --mem=20000
#SBATCH --workdir="/mnt/SCRATCH/"

function cleanup (){{
    echo "cleanup tmp data";
    sudo rm -rf $basedir;
}}

job_uuid="{JOB_UUID}"
psql_conf="/mnt/nfs/reference/postgres_config"
basedir=`sudo mktemp -d post_freebayes_qc.XXXXXXXXXX -p /mnt/SCRATCH/`
bed="{BED}"
vcf="{VCF}"
repository="git@github.com:uc-cdis/genomel_pipelines.git"
sudo chown ubuntu:ubuntu $basedir

cd $basedir

sudo git clone -b feat/retry $repository genomel_pipelines
sudo chown ubuntu:ubuntu -R genomel_pipelines

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python \
$basedir/genomel_pipelines/genomel/slurm/genomel_post_freebayes_qc.py \
--basedir $basedir \
--job_uuid $job_uuid \
--psql_conf $psql_conf \
--bed $bed \
--cwlwf $basedir/genomel_pipelines/genomel/cwl/workflows/variant_calling/post_freebayes.cwl \
--vcf $vcf
