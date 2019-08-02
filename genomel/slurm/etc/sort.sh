#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --ntasks=1
#SBATCH --workdir="/mnt/nfs/post_freebayes_qc"

chr="chr1"
basedir=`mktemp -d sort.${chr}.XXXXXXXXXX -p /mnt/nfs/post_freebayes_qc`
cwl="/mnt/nfs/cromwell_workdir/genomel_pipelines/genomel/cwl/tools/variant_calling/picard_sortvcf.cwl"
json="/mnt/nfs/post_freebayes_qc/${chr}.sort.json"

cd $basedir

/home/ubuntu/.virtualenvs/p2/bin/cwltool \
--debug \
--relax-path-checks \
--outdir $basedir \
--tmpdir-prefix /mnt/nfs/post_freebayes_qc/tmp/ \
--tmp-outdir-prefix /mnt/nfs/post_freebayes_qc/tmp/ \
$cwl \
$json