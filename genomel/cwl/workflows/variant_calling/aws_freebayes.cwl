#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  bam:
    type: File
    secondaryFiles: [^.bai]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  bed_file: File
  thread_count: int
  number_of_chunks: int
  output_prefix: string

outputs:
  time_metrics_from_freebayes:
    type: File
    outputSource: aws_freebayes/time_metrics
  time_metrics_from_picard_sortvcf:
    type: File
    outputSource: picard_sortvcf/time_metrics
  time_metrics_from_selectvariants:
    type: File
    outputSource: gatk3_selectvariants/time_metrics
  log_file:
    type: File
    outputSource: aws_freebayes/log_file
  freebayes_vcf:
    type: File
    outputSource: gatk3_selectvariants/output_vcf
  passed_bed:
    type: File[]
    outputSource: extract_pass_pair/passed_bed_list

steps:
  aws_freebayes:
    run: ../../tools/variant_calling/aws_freebayes.cwl
    in:
      job_uuid: job_uuid
      bam: bam
      reference: reference
      bed_file: bed_file
      thread_count: thread_count
      number_of_chunks: number_of_chunks
    out: [vcf_list, bed_list, log_file, time_metrics]

  extract_pass_pair:
    run: ../../tools/utils/extract_pass_pair.cwl
    in:
      bed_files: aws_freebayes/bed_list
      vcf_files: aws_freebayes/vcf_list
      log_file: aws_freebayes/log_file
    out: [ passed_vcf_list, passed_bed_list ]

  picard_sortvcf:
    run: ../../tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: extract_pass_pair/passed_vcf_list
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        source: output_prefix
        valueFrom: $(self + '.srt')
    out: [sorted_vcf, time_metrics]

  gatk3_selectvariants:
    run: ../../tools/variant_calling/gatk3_selectvariants.cwl
    in:
      job_uuid: job_uuid
      input_vcf: picard_sortvcf/sorted_vcf
      reference: reference
      output_prefix:
        source: [job_uuid, output_prefix]
        valueFrom: $(self[0] + '.' + self[1] + '.freebayes')
    out: [output_vcf, time_metrics]
