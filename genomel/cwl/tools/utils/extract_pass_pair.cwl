#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/genomel_variant_calling:6.0

inputs:
  bed_files:
    type:
      type: array
      items: File
      inputBinding:
        prefix: -b
    inputBinding:
      position: 0

  vcf_files:
    type:
      type: array
      items: File
      inputBinding:
        prefix: -v
    inputBinding:
      position: 1

  log_file:
    type: File
    inputBinding:
      prefix: -l
      position: 2

outputs:
  passed_vcf_list:
    type: File[]
    outputBinding:
      glob: '*.vcf'

  passed_bed_list:
    type: File[]
    outputBinding:
      glob: '*.bed'

baseCommand: ['python', '/opt/extract_pass_pair.py']
