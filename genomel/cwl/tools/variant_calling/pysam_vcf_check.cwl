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

stdout: count
outputs:
  vcf_count:
    type: string
    outputBinding:
      glob: count
      loadContents: true
      outputEval: |
       ${
          var count = self[0].contents.trim()
          return count
       }

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      python /opt/pysam_vcf_check.py $(inputs.vcf.path)