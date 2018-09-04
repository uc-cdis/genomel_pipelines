## GenoMEL pipelines in Bionimbus

General workflow:

![alt text](https://github.com/uc-cdis/cwl/blob/feat/develop/docs/genomel_general_workflow.png "General-workflow")

Workon:
* Revamp variant calling docker/workflow.
  > Merge three callers into one, and make parallelization inside docker. Increase scalability and automation potential.

* Rebuild docker.
  > Ideally lessen layers and burdens in docker. Reduce the image size and potentially shorten the speed of accessing docker at first time.

* Conditional workflow.
  > Merge all individual workflows together. Put conditions so that input could be either fasta, or bam, and conditions to choose the path of the workflows.
