#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: alpine

inputs:
  bed_file: File
  number_of_lines_per_chunk: int

outputs:
  bed_files:
    type: File[]
    outputBinding:
      glob: "bed_part_*"

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      split -l $(inputs.number_of_lines_per_chunk) $(inputs.bed_file.path) bed_part_
