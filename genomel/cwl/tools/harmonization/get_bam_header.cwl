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
  bam:
    type: File
    doc: Input bam file

stdout: old_header
outputs:
  bam_header:
    type: stdout

baseCommand: []
arguments:
  - valueFrom: >-
      samtools view -H $(inputs.bam.path)
    shellQuote: False
