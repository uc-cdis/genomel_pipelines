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
  input_bam: File
  nthreads: int
  dbname: File
  reference_fai_index: File

outputs:
  time_metrics_from_bam_to_fastq:
    type: File
    outputSource: bam_to_fastq/time_metrics
  time_metrics_from_trim_adaptor:
    type: File[]
    outputSource: trim_adaptor/time_metrics
  time_metrics_from_novoalign_filter_dedup:
    type: File[]
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
  get_readgroup_info:
    run: ../tools/harmonization/get_readgroup_name.cwl
    in:
      bam: input_bam
    out: [readgroup_lines, readgroup_names]

  bam_to_fastq:
    run: ../tools/harmonization/bam_to_fastq.cwl
    in:
      job_uuid: job_uuid
      readgroup_lines: get_readgroup_info/readgroup_lines
      readgroup_names: get_readgroup_info/readgroup_names
      filename: input_bam
    out: [output_readgroup_lines, output_readgroup_names, output_fastq1, output_fastq2, time_metrics]

  trim_adaptor:
    run: ../tools/harmonization/trimmomatic.cwl
    scatter: [readgroup_line, readgroup_name, input_read1_fastq_file, input_read2_fastq_file]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      readgroup_line: bam_to_fastq/output_readgroup_lines
      readgroup_name: bam_to_fastq/output_readgroup_names
      input_read1_fastq_file: bam_to_fastq/output_fastq1
      input_read2_fastq_file: bam_to_fastq/output_fastq2
    out: [paired_readgroup_line, paired_readgroup_name, output_read1_trimmed_file, output_read2_trimmed_file, time_metrics]

  get_fai_bed:
    run: ../tools/harmonization/fai_to_bed.cwl
    in:
      ref_fai:
        source: reference_fai_index
    out: [output_bed]

  novoalign_filter_dedup:
    run: ../tools/harmonization/novoalign.cwl
    scatter: [input_read1_fastq_file, input_read2_fastq_file, readgroup, output_name]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      nthreads: nthreads
      dbname: dbname
      input_read1_fastq_file: trim_adaptor/output_read1_trimmed_file
      input_read2_fastq_file: trim_adaptor/output_read2_trimmed_file
      readgroup: trim_adaptor/paired_readgroup_line
      output_name: trim_adaptor/paired_readgroup_name
    out: [readgroup_bam, time_metrics]

  readgroups_merge:
    run: ../tools/harmonization/sambamba_merge.cwl
    in:
      job_uuid: job_uuid
      bams: novoalign_filter_dedup/readgroup_bam
      base_file_name:
        source: job_uuid
        valueFrom: $(self)
    out: [merged_bam, time_metrics]

  get_bam_new_header:
    run: ../tools/harmonization/get_bam_new_header.cwl
    in:
      bam: readgroups_merge/merged_bam
    out: [bam_new_header]

  bam_reheader:
    run: ../tools/harmonization/samtools_reheader.cwl
    in:
      job_uuid: job_uuid
      new_header: get_bam_new_header/bam_new_header
      interval_bed: get_fai_bed/output_bed
      bam: readgroups_merge/merged_bam
    out: [reheadered_bam, time_metrics]

  bam_sort:
    run: ../tools/harmonization/sambamba_sort.cwl
    in:
      job_uuid: job_uuid
      bam: bam_reheader/reheadered_bam
      base_file_name:
        source: job_uuid
        valueFrom: $(self)
    out: [sorted_bam, time_metrics]
