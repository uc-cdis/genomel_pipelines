#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_bwa:1.0

inputs:
  job_uuid: string

  bams:
    type: File[]
    inputBinding:
      position: 99
      shellQuote: false

  base_file_name: string

outputs:
  merged_bam:
    type: File
    outputBinding:
      glob: '*.bam'

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.SambambaMerge' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.SambambaMerge' + '.time.json')
        /opt/sambamba-0.6.8-linux-static merge -t 64 $(inputs.base_file_name).merged.bam


