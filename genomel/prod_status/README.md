### GenoMEL-Bionimbus Protected Data Cloud (PDC) Freebayes production tracker

Freebayes production status tracker
[Production status](https://github.com/uc-cdis/genomel_pipelines/blob/feat/retry/genomel/prod_status/bionimbus_pdc_freebayes_production_status.pdf "Production status")

This pdf will automatically regenerate hourly to keep track of the status of freebayes production. All the estimations will be updated hourly as well based on up-to-date metrics.

#### Expected days on current run:

It's the number of days we estimated to complete the current running round based on metrics we gathered from the current run. Since we tried to higher the throughput, we expected there would have some chunks of jobs failed because of out of memory issue. The workflow can handle these cases perfectly, and we will rerun these failed chunks on the second production run.

#### Expected days on completion:

It's the number of days we estimated to complete the whole GenoMEL freebayes pipeline, which is combined days with current run and the second run. The number of failed chunks is a rough estimation, so the time on second run is just a very rough guesstimation.