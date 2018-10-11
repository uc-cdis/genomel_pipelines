#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization:1.0
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  - id: input_bam_path
    type: File
    doc: Input bam file
    inputBinding:
      position: 2

stdout: readgroups_header
outputs:
  - id: readgroup_lines
    type: string[]
    outputBinding:
      glob: readgroups_header
      loadContents: true
      outputEval: $(self[0].contents.trim().split('\n'))

  - id: readgroup_names
    type: string[]
    outputBinding:
      glob: readgroups_header
      loadContents: true
      outputEval: |
        ${
          var rg_name = [];
          for (var i = 0; i < self[0].contents.trim().split('\n').length; i++){
            rg_name.push(self[0].contents.trim().split('\n')[i].split('\t')[1].replace('ID:', ''))
          };
          return rg_name
        }

baseCommand: ['samtools', 'view', '-H']
arguments:
  - valueFrom: 'grep ^@RG'
    position: 3
    prefix: "|"
    shellQuote: False
