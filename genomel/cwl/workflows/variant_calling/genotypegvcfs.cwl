#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  gvcf_file: File[]
  reference:
    type: File
    secondaryFiles:
      - '.fai'
      - '^.dict'
  interval: File
  snp_ref:
    type: File
    secondaryFiles: '.tbi'

outputs:
  time_metrics_from_gatk3_genotypegvcfs:
    type: File
    outputSource: gatk3_genotypegvcfs/time_metrics
  time_metrics_from_picard_sortvcf:
    type: File
    outputSource: picard_sortvcf/time_metrics
  genotypegvcfs_sorted_vcf:
    type: File
    outputSource: picard_sortvcf/sorted_vcf

steps:
  gatk3_genotypegvcfs:
    run: ../../tools/variant_calling/gatk3_genotypegvcfs.cwl
    in:
      job_uuid: job_uuid
      gvcf_file: gvcf_file
      reference: reference
      interval: interval
      snp_ref: snp_ref
    out: [vcf_list, time_metrics]

  picard_sortvcf:
    run: ../../tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: gatk3_genotypegvcfs/vcf_list
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        valueFrom: 'genotypegvcfs.srt'
    out: [sorted_vcf, time_metrics]
