#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/genomel_variant_calling:6.0

inputs:
  input_files:
    type: File[]
    inputBinding:
      position: 0
  output_file: string

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.output_file)

baseCommand: cat
stdout: $(inputs.output_file)