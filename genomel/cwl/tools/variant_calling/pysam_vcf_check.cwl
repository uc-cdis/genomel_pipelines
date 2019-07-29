#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/cdis/pysam_vcf_check:1.0

inputs:
  vcf: File
  output_name: string

outputs:
  vcf_count:
    type: File
    outputBinding:
      glob: $(inputs.output_name)

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      python /opt/pysam_vcf_check.py $(inputs.vcf.path) > $(inputs.output_name)