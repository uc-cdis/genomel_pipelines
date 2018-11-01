#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  input_bam: File

outputs:
  time_metrics_from_bam_to_fastq:
    type: File
    outputSource: bam_to_fastq/time_metrics
  output_readgroup_lines:
    type: string[]
    outputSource: bam_to_fastq/output_readgroup_lines
  output_readgroup_names:
    type: string[]
    outputSource: bam_to_fastq/output_readgroup_names
  output_fastq1:
    type: File[]
    outputSource: bam_to_fastq/output_fastq1
  output_fastq2:
    type: File[]
    outputSource: bam_to_fastq/output_fastq2

steps:
  get_readgroup_info:
    run: ../../tools/harmonization/get_readgroup_name.cwl
    in:
      bam: input_bam
    out: [readgroup_lines, readgroup_names]

  bam_to_fastq:
    run: ../../tools/harmonization/bam_to_fastq.cwl
    in:
      job_uuid: job_uuid
      readgroup_lines: get_readgroup_info/readgroup_lines
      readgroup_names: get_readgroup_info/readgroup_names
      filename: input_bam
    out: [output_readgroup_lines, output_readgroup_names, output_fastq1, output_fastq2, time_metrics]
