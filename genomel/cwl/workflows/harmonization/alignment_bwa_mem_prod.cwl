#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: ScatterFeatureRequirement

inputs:
  job_uuid: string
  input_read1: File[]
  input_read2: File[]
  readgroup_lines: string[]
  readgroup_names: string[]
  reference:
    type: File
    secondaryFiles: [.fai, .64.amb, .64.ann, .64.bwt, .64.pac, .64.sa, ^.dict, .amb, .ann, .bwt, .pac, .sa]

outputs:
  time_metrics_from_trim_adaptor:
    type: File[]
    outputSource: trim_adaptor/time_metrics
  time_metrics_from_bwa_mem:
    type: File[]
    outputSource: bwa_mem/time_metrics
  time_metrics_from_merge:
    type: File
    outputSource: readgroups_merge/time_metrics
  time_metrics_from_mrkdup:
    type: File
    outputSource: bam_mrkdup/time_metrics
  time_metrics_from_sort:
    type: File
    outputSource: bam_sort/time_metrics
  sorted_bam:
    type: File
    outputSource: bam_sort/sorted_bam

steps:
  trim_adaptor:
    run: ../../tools/harmonization/trimmomatic.cwl
    scatter: [readgroup_line, readgroup_name, input_read1_fastq_file, input_read2_fastq_file]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      readgroup_line: readgroup_lines
      readgroup_name: readgroup_names
      input_read1_fastq_file: input_read1
      input_read2_fastq_file: input_read2
    out: [paired_readgroup_line, paired_readgroup_name, output_read1_trimmed_file, output_read2_trimmed_file, time_metrics]

  bwa_mem:
    run: ../../tools/harmonization/bwa_mem_only.cwl
    scatter: [input_read1_fastq_file, input_read2_fastq_file, readgroup_line, readgroup_name]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      reference: reference
      input_read1_fastq_file: trim_adaptor/output_read1_trimmed_file
      input_read2_fastq_file: trim_adaptor/output_read2_trimmed_file
      readgroup_line: trim_adaptor/paired_readgroup_line
      readgroup_name: trim_adaptor/paired_readgroup_name
    out: [readgroup_bam, time_metrics]

  readgroups_merge:
    run: ../../tools/harmonization/sambamba_merge.cwl
    in:
      job_uuid: job_uuid
      bams: bwa_mem/readgroup_bam
      base_file_name:
        source: job_uuid
        valueFrom: $(self)
    out: [merged_bam, time_metrics]

  bam_mrkdup:
    run: ../../tools/harmonization/markduplicates_on_bam.cwl
    in:
      job_uuid: job_uuid
      bam: readgroups_merge/merged_bam
    out: [mrkdup_bam, time_metrics]

  bam_sort:
    run: ../../tools/harmonization/sambamba_sort.cwl
    in:
      job_uuid: job_uuid
      bam: bam_mrkdup/mrkdup_bam
      base_file_name:
        source: job_uuid
        valueFrom: $(self)
    out: [sorted_bam, time_metrics]
