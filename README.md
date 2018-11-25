## GenoMEL-Bionimbus Protected Data Cloud (PDC) production pipeline

General workflow:

![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/docs/genomel_individual_workflow.png "individual")
![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/docs/genomel_cohort_calling.png "cohort")

GenoMEL individual aliquot workflow:

* ![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/cwl/genomel_individual_workflow.cwl "Main CWL workflow runner")

* ![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/slurm/etc/template.json "CWL runner input json template")

* ![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/slurm/genomel_individual_aliquot_runner.py "Main SLURM python runner")

* ![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/slurm/etc/template.sh "SLURM SBATCH job template")
