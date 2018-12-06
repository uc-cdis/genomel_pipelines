#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  bam_files:
    type: File[]
    secondaryFiles: [^.bai]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  bed_file: File
  thread_count: int
  output_prefix: string

outputs:
  time_metrics_from_freebayes:
    type: File
    outputSource: genomel_pdc_freebayes/time_metrics
  time_metrics_from_picard_sortvcf:
    type: File
    outputSource: picard_sortvcf/time_metrics
  time_metrics_from_selectvariants:
    type: File
    outputSource: gatk3_selectvariants/time_metrics
  freebayes_vcf:
    type: File
    outputSource: gatk3_selectvariants/output_vcf

steps:
  genomel_pdc_freebayes:
    run: ../../tools/variant_calling/genomel_pdc_freebayes.cwl
    in:
      job_uuid: job_uuid
      bam_files: bam_files
      reference: reference
      bed_file: bed_file
      thread_count: thread_count
    out: [vcf_list, time_metrics]

  picard_sortvcf:
    run: ../../tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: genomel_pdc_freebayes/vcf_list
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
        valueFrom: $(self[0] + '.' + self[1])
    out: [output_vcf, time_metrics]
