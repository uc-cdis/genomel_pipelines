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
  readgroups_to_replace:
    type: string[]
    inputBinding:
      prefix: --problem_rg
      position: 98
      shellQuote: false
  new_readgroups:
    type: string[]
    inputBinding:
      prefix: --new_rg
      position: 99
      shellQuote: false

outputs:
  bam_new_header:
    type: File
    outputBinding:
      glob: 'new_header'

baseCommand: []
arguments:
  - valueFrom: >-
      python /opt/rg_fix.py --old_header $(inputs.old_header.path)
    shellQuote: False
