#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_bwa:1.0
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  bam: File

outputs:
  mrkdup_bam:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.mrkdup.bam')

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.SamtoolsFilter_SamblasterMrkdup' + '.time.json')

baseCommand: []
arguments:
  - shellQuote: False
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.SamtoolsFilter_SamblasterMrkdup' + '.time.json')
      samtools view -@ 32 -Sh -f 3 $(inputs.bam.path)
      | /opt/samblaster-v.0.1.24/samblaster -M -i /dev/stdin -o /dev/stdout
      | /opt/sambamba-0.6.8-linux-static view -t 30 -f bam -S -o $(inputs.job_uuid).mrkdup.bam /dev/stdin
