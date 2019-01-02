#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: ResourceRequirement
    coresMin: 30
    coresMax: 30

inputs:
  job_uuid: string
  gvcf_files:
    type: File[]
    secondaryFiles: [.tbi]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  bed_file: File
  thread_count: int
  number_of_chunks: int
  output_prefix: string

outputs:
  time_metrics_from_gatk4_cohort_genotyping:
    type: File
    outputSource: genomel_pdc_gatk4_cohort_genotyping/time_metrics
  time_metrics_from_picard_sortvcf:
    type: File
    outputSource: picard_sortvcf/time_metrics
  time_metrics_from_selectvariants:
    type: File
    outputSource: gatk3_selectvariants/time_metrics
  gatk4_cohort_genotyping_vcf:
    type: File
    outputSource: gatk3_selectvariants/output_vcf

steps:
  genomel_pdc_gatk4_cohort_genotyping:
    run: ../../tools/variant_calling/genomel_gatk4_cohort_genotyping.cwl
    in:
      job_uuid: job_uuid
      gvcf_files: gvcf_files
      reference: reference
      bed_file: bed_file
      thread_count: thread_count
      number_of_chunks: number_of_chunks
    out: [vcf_list, time_metrics]

  picard_sortvcf:
    run: ../../tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: genomel_pdc_gatk4_cohort_genotyping/vcf_list
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
        valueFrom: $(self[0] + '.' + self[1] + '.gatk4')
    out: [output_vcf, time_metrics]
