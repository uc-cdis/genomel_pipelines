#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization@sha256:2e2fe50befce7f34f80e54036e93aa195627eeba2256a83ee36f4e713f2f43ce
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  bam:
    type: File
    doc: Input bam file

stdout: new_header
outputs:
  bam_new_header:
    type: stdout

baseCommand: []
arguments:
  - valueFrom: >-
      samtools view -H $(inputs.bam.path) | grep -v "SN:phiX174"
    shellQuote: False
