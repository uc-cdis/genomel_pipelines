#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/cdis/genomel_readgroup_fix:1.0
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  old_header:
    type: File
  aliquot_id: string
outputs:
  bam_new_header:
    type: File
    outputBinding:
      glob: 'new_header'

baseCommand: []
arguments:
  - valueFrom: >-
      python /opt/rg_fix.py --old_header $(inputs.old_header.path) --aliquot_id $(inputs.aliquot_id)
    shellQuote: False
