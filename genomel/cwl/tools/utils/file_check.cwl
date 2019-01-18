#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-tools/alpine:1.0

inputs:
  file: File
  md5sum: string

stdout: file_md5
outputs:
  output:
    type: File?
    outputBinding:
      glob: file_md5
      loadContents: true
      outputEval: |
        ${
          var local_md5 = self[0].contents.trim().split(' ')[0]
          if (inputs.md5sum != local_md5){
            return null
          } else {
            return inputs.file
          }
        }

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      md5sum $(inputs.file.path)
