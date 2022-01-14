# Notice: all the docker tages are temporarily removed due to the log4j vulnerability. The workflow can not be run as is until the log4j issue is resolved.

## GenoMEL-Bionimbus Protected Data Cloud (PDC) production pipeline

General workflow:

<img src="https://github.com/uc-cdis/cwl/blob/master/docs/genomel_individual_workflow.png" width="460.5" height="363"> <img src="https://github.com/uc-cdis/cwl/blob/master/docs/genomel_cohort_calling.png" width="397.5" height="363">

GenoMEL individual aliquot workflow:

* [Individual CWL workflow runner](https://github.com/uc-cdis/cwl/blob/master/genomel/genomel_individual_workflow.cwl "Individual CWL workflow runner")

* [Individual CWL runner input json template](https://github.com/uc-cdis/cwl/blob/master/genomel/slurm/etc/template.json "Individual CWL runner input json template")

* [Individual workflow SLURM python runner](https://github.com/uc-cdis/cwl/blob/master/genomel/slurm/genomel_individual_aliquot_runner.py "Individual workflow SLURM python runner")

* [individual workflow SLURM SBATCH job template](https://github.com/uc-cdis/cwl/blob/master/genomel/slurm/etc/template.sh "Individual workflow SLURM SBATCH job template")

GenoMEL cohort genotyping workflow

* [Cohort level CWL workflow runner](https://github.com/uc-cdis/cwl/blob/master/genomel/genomel_cohort_genotyping.cwl "Cohort level CWL workflow runner")

* [Cohort level CWL runner input json template](https://github.com/uc-cdis/cwl/blob/master/genomel/slurm/etc/cohort_genotyping.json "Cohort level CWL runner input json template")

* [Cohort level SLURM python runner](https://github.com/uc-cdis/cwl/blob/master/genomel/slurm/genomel_cohort_genotyping_runner.py "Cohort level SLURM python runner")

* [Cohort level SLURM SBATCH job template](https://github.com/uc-cdis/cwl/blob/master/genomel/slurm/etc/cohort_genotyping.sh "Cohort level SLURM SBATCH job template")
