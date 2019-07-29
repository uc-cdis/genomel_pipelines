#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  vcf: File
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  output_prefix: string

outputs:
  raw_counts:
    type: File
    outputSource: raw_vcf_count/vcf_count
  filtered_vcf:
    type: File
    secondaryFiles: [.tbi]
    outputSource: vcf_filtration/output_vcf
  filtered_counts:
    type: File
    outputSource: filtered_vcf_count/vcf_count

steps:
  raw_vcf_count:
    run: ../../tools/variant_calling/pysam_vcf_check.cwl
    in:
      vcf: vcf
      output_name:
        valueFrom: "raw_count"
    out: [ vcf_count ]

  vcf_filtration:
    run: ../../tools/variant_calling/post_freebayes_filtration.cwl
    in:
      job_uuid: job_uuid
      input_vcf: vcf
      reference: reference
      output_prefix: output_prefix
    out: [ output_vcf, time_metrics ]

  filtered_vcf_count:
    run: ../../tools/variant_calling/pysam_vcf_check.cwl
    in:
      vcf: vcf_filtration/output_vcf
      output_name:
        valueFrom: "filtered_count"
    out: [ vcf_count ]