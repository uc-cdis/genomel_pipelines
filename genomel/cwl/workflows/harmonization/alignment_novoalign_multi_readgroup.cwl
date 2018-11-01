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
  interval_bed: File
  input_read1: File[]
  input_read2: File[]
  readgroup_lines: string[]
  readgroup_names: string[]
  nthreads: int
  dbname: File
  reference_fai_index: File

outputs:
  time_metrics_from_trim_adaptor:
    type: File[]
    outputSource: trim_adaptor/time_metrics
  time_metrics_from_novoalign_filter_dedup:
    type: File
    outputSource: novoalign_filter_dedup/time_metrics
  time_metrics_from_merge:
    type: File
    outputSource: readgroups_merge/time_metrics
  time_metrics_from_sort:
    type: File
    outputSource: bam_sort/time_metrics
  time_metrics_from_reheader:
    type: File
    outputSource: bam_reheader/time_metrics
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

  novoalign_filter_dedup:
    run: ../../tools/harmonization/novoalign_multi_readgroup.cwl
    in:
      job_uuid: job_uuid
      nthreads: nthreads
      dbname: dbname
      input_read1_fastq_files: trim_adaptor/output_read1_trimmed_file
      input_read2_fastq_files: trim_adaptor/output_read2_trimmed_file
      readgroup_lines: trim_adaptor/paired_readgroup_line
      readgroup_names: trim_adaptor/paired_readgroup_name
    out: [readgroup_bam, time_metrics]

  readgroups_merge:
    run: ../../tools/harmonization/sambamba_merge.cwl
    in:
      job_uuid: job_uuid
      bams: novoalign_filter_dedup/readgroup_bam
      base_file_name:
        source: job_uuid
        valueFrom: $(self)
    out: [merged_bam, time_metrics]

  get_bam_new_header:
    run: ../../tools/harmonization/get_bam_new_header.cwl
    in:
      bam: readgroups_merge/merged_bam
    out: [bam_new_header]

  bam_reheader:
    run: ../../tools/harmonization/samtools_reheader.cwl
    in:
      job_uuid: job_uuid
      new_header: get_bam_new_header/bam_new_header
      interval_bed: interval_bed
      bam: readgroups_merge/merged_bam
    out: [reheadered_bam, time_metrics]

  bam_sort:
    run: ../../tools/harmonization/sambamba_sort.cwl
    in:
      job_uuid: job_uuid
      bam: bam_reheader/reheadered_bam
      base_file_name:
        source: job_uuid
        valueFrom: $(self)
    out: [sorted_bam, time_metrics]
