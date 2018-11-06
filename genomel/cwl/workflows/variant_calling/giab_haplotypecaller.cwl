#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  bam_file:
    type: File
    secondaryFiles: [^.bai]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]

  interval: File
  snp_ref:
    type: File
    secondaryFiles: [.tbi]

outputs:
  time_metrics_from_gatk3_giab_haplotypecaller:
    type: File
    outputSource: gatk3_giab_haplotypecaller/time_metrics
  time_metrics_from_picard_sortvcf:
    type: File
    outputSource: picard_sortvcf/time_metrics
  haplotypecaller_sorted_vcf:
    type: File
    outputSource: picard_sortvcf/sorted_vcf

steps:
  gatk3_giab_haplotypecaller:
    run: ../../tools/variant_calling/gatk3_giab_haplotypercaller.cwl
    in:
      job_uuid: job_uuid
      bam_file: bam_file
      reference: reference
      interval: interval
      snp_ref: snp_ref
    out: [vcf_list, time_metrics]

  picard_sortvcf:
    run: ../../tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: gatk3_giab_haplotypecaller/vcf_list
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        valueFrom: 'giab.haplotypecaller'
    out: [sorted_vcf, time_metrics]
