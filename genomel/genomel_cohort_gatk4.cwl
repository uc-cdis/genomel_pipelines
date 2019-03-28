#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  job_uuid: string
  bed_files: File[]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  cromwell_engine: boolean

  ###GATK4
  gvcf_files:
    type: File[]
    secondaryFiles: [.tbi]
  gatk4_genotyping_thread_count: int
  number_of_chunks_for_gatk: int

  ###Upload
  aws_config: File
  aws_shared_credentials: File
  upload_s3_profile: string
  upload_s3_endpoint: string
  upload_s3_bucket: string

outputs:
  gatk4_vcf:
    type: File
    outputSource: sort_gatk4/sorted_vcf

  time_logs:
    type: File[]
    outputSource: extract_time_log/output

steps:
  gatk4_cohort_genotyping:
    run: ./cwl/workflows/variant_calling/gatk4_cohort_genotyping.cwl
    scatter: [bed_file, output_prefix]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      gvcf_files: gvcf_files
      reference: reference
      bed_file: bed_files
      thread_count: gatk4_genotyping_thread_count
      number_of_chunks: number_of_chunks_for_gatk
      output_prefix:
        source: bed_files
        valueFrom: $(self.nameroot)
      cromwell_engine: cromwell_engine
    out: [time_metrics_from_gatk4_cohort_genotyping,
          time_metrics_from_picard_sortvcf,
          time_metrics_from_selectvariants,
          gatk4_cohort_genotyping_vcf]

  sort_gatk4:
    run: ./cwl/tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: gatk4_cohort_genotyping/gatk4_cohort_genotyping_vcf
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        valueFrom: 'genomel_cohort.gatk4.genomel_all'
    out: [sorted_vcf, time_metrics]

  upload_gatk4_vcf:
    run: ./cwl/tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input: sort_gatk4/sorted_vcf
      s3uri:
        source: [upload_s3_bucket, sort_gatk4/sorted_vcf]
        valueFrom: $(self[0])/$(self[1].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  upload_gatk4_vcf_index:
    run: ./cwl/tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input:
        source: sort_gatk4/sorted_vcf
        valueFrom: $(self.secondaryFiles[0])
      s3uri:
        source: [upload_s3_bucket, sort_gatk4/sorted_vcf]
        valueFrom: $(self[0])/$(self[1].secondaryFiles[0].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  extract_time_log:
    run: ./cwl/tools/utils/extract_outputs.cwl
    in:
      file_array:
        source: [gatk4_cohort_genotyping/time_metrics_from_gatk4_cohort_genotyping,
                 gatk4_cohort_genotyping/time_metrics_from_picard_sortvcf,
                 gatk4_cohort_genotyping/time_metrics_from_selectvariants,
                 sort_gatk4/time_metrics,
                 upload_gatk4_vcf/time_metrics,
                 upload_gatk4_vcf_index/time_metrics]
        valueFrom: |
          ${
            var log_list = []
            for (var i = 0; i < self.length; i++){
              if (Array.isArray(self[i])){
                if (Array.isArray(self[i][0])){
                  for (var j = 0; j < self[i][0].length; j++){
                    log_list.push(self[i][0][j])
                  }
                } else { log_list.push(self[i][0]) }
              } else {
                log_list.push(self[i])
              }
            }
            return log_list
          }
    out: [output]
