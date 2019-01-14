#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-tools/alpine:1.0
  - class: InitialWorkDirRequirement
    listing:
      - entryname: "test.conf"
        entry: |
          ${
            var paths = [];
            for (var i = 0; i < inputs.bam_path.length; i++){
              if (inputs.bam_path[i]["nameext"] == ".bam"){
                paths.push(inputs.bam_path[i]["path"])
                }
              }
            return paths.join("\n");
            }

inputs:
  bam_path:
    type: File[]
    secondaryFiles: [^.bai]

outputs:
  output:
    type: File
    outputBinding:
      glob: "test.conf"

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      sed -i "s/\\\\n/\\n/g" test.conf
