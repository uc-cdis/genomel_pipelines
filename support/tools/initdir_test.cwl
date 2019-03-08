#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/cdis/samtools@sha256:8e70e8ace2b94cf6741602feaddee24fefc914675c58f539cade6c390b2fab4d
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input_bam)
        entryname: $(inputs.input_bam.basename)

inputs:
  input_bam:
    type: File
    inputBinding:
      position: 1
      valueFrom: $(self.basename)

outputs:
  bam_with_index:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename)
    secondaryFiles:
      - '.bai'

baseCommand: ['samtools', 'index']
