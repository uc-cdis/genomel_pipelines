#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: InitialWorkDirRequirement
    listing:
      - entryname: $(inputs.bam.basename)
        entry: $(inputs.bam)
      - entryname: $(inputs.bam_index.basename)
        entry: $(inputs.bam_index)
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

class: CommandLineTool

inputs:
  - id: bam
    type: File

  - id: bam_index
    type: File

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.bam.basename)
    secondaryFiles:
      - .bai

baseCommand: "true"
