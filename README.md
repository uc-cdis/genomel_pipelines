## GenoMEL-Bionimbus Protected Data Cloud (PDC) production pipeline

General workflow:

<img src="https://github.com/uc-cdis/cwl/blob/feat/develop/docs/genomel_individual_workflow.png" width="460.5" height="363"> <img src="https://github.com/uc-cdis/cwl/blob/feat/develop/docs/genomel_cohort_calling.png" width="397.5" height="363">

GenoMEL individual aliquot workflow:

* [Main CWL workflow runner](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/cwl/genomel_individual_workflow.cwl "Main CWL workflow runner")

* [CWL runner input json template](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/slurm/etc/template.json "CWL runner input json template")

* [Main SLURM python runner](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/slurm/genomel_individual_aliquot_runner.py "Main SLURM python runner")

* [SLURM SBATCH job template](https://github.com/uc-cdis/cwl/blob/feat/develop/genomel/slurm/etc/template.sh "SLURM SBATCH job template")
