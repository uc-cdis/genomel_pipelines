#!/usr/bin/env cwl-runner


### Kevin cwl for
# Duplication Removal (Lane or Sample Level)
# Sample Level Duplication Removal

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


          











  - valueFrom: $(inputs.input_read1_fastq_file.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + '.trimmed.fastq')
    position: 7
  - valueFrom: |
      ${
        if (inputs.end_mode == "PE" && inputs.input_read2_fastq_file)
          return inputs.input_read1_fastq_file.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + '.trimmed.unpaired.fastq';
        return null;
      }
    position: 8
  - valueFrom: |
      ${
        if (inputs.end_mode == "PE" && inputs.input_read2_fastq_file)
          return inputs.input_read2_fastq_file.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + '.trimmed.fastq';
        return null;
      }
    position: 9
  - valueFrom: |
      ${
        if (inputs.end_mode == "PE" && inputs.input_read2_fastq_file)
          return inputs.input_read2_fastq_file.path.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, '') + '.trimmed.unpaired.fastq';
        return null;
      }
    position: 10
  - valueFrom: $("ILLUMINACLIP:" + inputs.input_adapters_file.path + ":"+ inputs.illuminaclip)
    position: 11

description: |
  Trimmomatic is a fast, multithreaded command line tool that can be used to trim and crop
  Illumina (FASTQ) data as well as to remove adapters. These adapters can pose a real problem
  depending on the library preparation and downstream application.
  There are two major modes of the program: Paired end mode and Single end mode. The
  paired end mode will maintain correspondence of read pairs and also use the additional
  information contained in paired reads to better find adapter or PCR primer fragments
  introduced by the library preparation process.
  Trimmomatic works with FASTQ files (using phred + 33 or phred + 64 quality scores,
  depending on the Illumina pipeline used).
      


