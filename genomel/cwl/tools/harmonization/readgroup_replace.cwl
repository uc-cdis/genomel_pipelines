#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/cdis/genomel_readgroup_fix:1.1
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input_bam)
        entryname: $(inputs.input_bam.basename)

inputs:
  old_header: File
  aliquot_id: string
  input_bam: File
  job_uuid: string
outputs:
  rg_fixed_bam:
    type: File
    outputBinding:
      glob: '*rg_fixed.bam'
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.PicardReheader' + '.time.json')

baseCommand: []
arguments:
  - shellQuote: False
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.PicardReheader' + '.time.json')
      python /opt/rg_fix.py
      --old_header $(inputs.old_header.path)
      --aliquot_id $(inputs.aliquot_id)
      --input_bam $(inputs.input_bam.path)
