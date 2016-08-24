#!/usr/bin/env cwl-runner

### Kevin cwl for
# Duplication Removal (Lane or Sample Level)
# Sample Level Duplication Removal

### NOTE
# 8-24-16 -- This CWL is not yet complete

cwlVersion: "cwl:draft-3"

#class: #NA (Tool) 

requirements:
  - $import: envvar-global.cwl
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis
  #- class: ScatterFeatureRequirement
  #- class: StepInputExpressionRequirement

inputs:
    - id: java_opts
      type: string
      default: "-Xmx16g"
      description: "JVM arguments should be a quoted, space separated list (e.g. \"-Xmx16g -Xms128m -Xmx512m\")"
      inputBinding:
        position: 1
        shellQuote: false
    - id: picard_jar_path
      type: file
      inputBinding:
        position: 2
        prefix: "-jar"
    - id: picard_tool
      type: file
        default: "MarkDuplicates"  # is this the way to do this - or is there a suffix-like inputBinding
        inputBinding:
          position: 3
    - id: input_bam_path
      type: File 
      inputBinding:
        position 4
        prefix: INPUT=
        separate: false
    - id: output_bam_filename # can't be same dir as input?
      type: string
      default:
        glob: |
          ${
            return inputs.input_bam_path.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + inputs.removal_type + '.duplicate_removed.bam';
           } 
      inputBinding:
        position 5
        prefix: INPUT=
        separate: false
    - id: output_metrics_filename = # can't be same dir as input?
      type: string
      glob: |
        ${
          return inputs.input_bam_path.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + inputs.removal_type + '.duplicate_removed.metrics.txt';
          }
      inputBinding:
        position 6
        prefix: METRICS_FILE=
        separate: false
    - id remove_duplicates # bool or string?
      type: string
      default: "true"
      description: |
        true|false
      inputbinding:
        position: 7
        prefix: REMOVE_DUPLICATES=
        separate: false
    - id create_index # bool or string?
      type: string
      default: "true"
      description: |
        true|false
      inputbinding:
        position: 8
        prefix: CREATE_INDEX=
        separate: false
    - id assume_sorted # bool or string?
      type: string
      default: "true"
      description: |
        true|false
      inputbinding:
        position: 9
        prefix: ASSUME_SORTED=
        separate: false  
    - id validation_stringency
      type: string
      default: "LENIENT"
      description: 
      inputbinding:
        position: 10
        prefix: VALIDATION_STRINGENCY=
    - id removal_type
      type: string
      default: "LLDR"
      description: |
        LLDR|SLDR
        <length>
        This module can be used to perform the (L)ane or (S)ample (L)evel (D)uplication (R)emoval.
        You must choose between one of these two options. 
        <length>
      inputbinding:
        position: 11
          
outputs:
      - id: duplicate_removed_output_bam 
      type: File
      outputBinding:
        glob: |
          ${
            return inputs.input_bam_path.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + inputs.removal_type + '.duplicate_removed.bam';
           }
      - id: duplicate_removed_output_metrics
      type: File
      outputBinding:
        glob: |
          ${
            return inputs.input_bam_path.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + inputs.removal_type + '.duplicate_removed.metrics.txt';
           }
      - id: duplicate_removed_output_bai 
      type: ['null', File]
      outputBinding:
        glob: |
          ${
            if(inputs.create_index=="true")
              return inputs.input_bam_path.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + inputs.removal_type + '.duplicate_removed.bai';
            return null;  
           }

baseCommand: java
description: |
  This module can perform (L)ane or (S)ample (L)evel (D)uplication (R)emoval
