#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_bwa:1.0

inputs:
  job_uuid: string

  readgroup_line: string

  readgroup_name: string

  input_read1_fastq_file:
    type: File
    doc: FASTQ file for input read1.

  input_read2_fastq_file:
    type: File
    doc: FASTQ file for read R2 in Paired End mode.

outputs:
  paired_readgroup_line:
    type: string
    outputBinding:
      outputEval: |
        ${ return inputs.readgroup_line }

  paired_readgroup_name:
    type: string
    outputBinding:
      outputEval: |
        ${ return inputs.readgroup_name }

  output_read1_trimmed_file:
    type: File
    outputBinding:
      glob: $(inputs.input_read1_fastq_file.nameroot.replace(/\.[^/.]+$/, "") + '.trimmed.fastq.gz')

  output_read2_trimmed_file:
    type: File
    outputBinding:
      glob: $(inputs.input_read2_fastq_file.nameroot.replace(/\.[^/.]+$/, "") + '.trimmed.fastq.gz')

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.trimmomatic.' + inputs.readgroup_name + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.trimmomatic.' + inputs.readgroup_name + '.time.json')
      java -Xmx32g -jar /opt/Trimmomatic-0.38/trimmomatic-0.38.jar
      PE
      -threads 24
      -phred33
      $(inputs.input_read1_fastq_file.path) $(inputs.input_read2_fastq_file.path)
      $(inputs.input_read1_fastq_file.nameroot.replace(/\.[^/.]+$/, "") + '.trimmed.fastq.gz') $(inputs.input_read1_fastq_file.nameroot.replace(/\.[^/.]+$/, "") + '.trimmed.unpaired.fastq.gz')
      $(inputs.input_read2_fastq_file.nameroot.replace(/\.[^/.]+$/, "") + '.trimmed.fastq.gz') $(inputs.input_read2_fastq_file.nameroot.replace(/\.[^/.]+$/, "") + '.trimmed.unpaired.fastq.gz')
      ILLUMINACLIP:/opt/Trimmomatic-0.38/adapters/TruSeq3-PE-2.fa:2:30:12
      LEADING:12
      TRAILING:12
      SLIDINGWINDOW:4:15
      MINLEN:36
