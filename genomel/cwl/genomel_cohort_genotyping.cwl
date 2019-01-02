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
  bed_file: File
  number_of_lines_per_chunk: int
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]

  ###GATK4
  gvcf_files:
    type: File[]
    secondaryFiles: [.tbi]
  gatk4_genotyping_thread_count: int
  number_of_chunks_for_gatk: int

  ###Freebayes
  bam_files:
    type: File[]
    secondaryFiles: [^.bai]
  freebayes_thread_count: int
  number_of_chunks_for_freebayes: int

  ###Variant ensemble
  config_json: File

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

  freebayes_vcf:
    type: File
    outputSource: sort_freebayes/sorted_vcf

  variant_ensemble_vcf:
    type: File
    outputSource: sort_ensemble/sorted_vcf

  time_logs:
    type: File[]
    outputSource: extract_time_log/output

steps:
  prepare_intervals:
    run: ./tools/utils/prepare_intervals.cwl
    in:
      bed_file: bed_file
      number_of_lines_per_chunk: number_of_lines_per_chunk
    out: [bed_files]

  gatk4_cohort_genotyping:
    run: ./workflows/variant_calling/gatk4_cohort_genotyping.cwl
    scatter: [bed_file, output_prefix]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      gvcf_files: gvcf_files
      reference: reference
      bed_file: prepare_intervals/bed_files
      thread_count: gatk4_genotyping_thread_count
      number_of_chunks: number_of_chunks_for_gatk
      output_prefix:
        source: prepare_intervals/bed_files
        valueFrom: $(self.nameroot)
    out: [time_metrics_from_gatk4_cohort_genotyping,
          time_metrics_from_picard_sortvcf,
          time_metrics_from_selectvariants,
          gatk4_cohort_genotyping_vcf]

  freebayes_cohort_genotyping:
    run: ./workflows/variant_calling/freebayes.cwl
    scatter: [bed_file, output_prefix]
    scatterMethod: dotproduct
    in:
      job_uuid: job_uuid
      bam_files: bam_files
      reference: reference
      bed_file: prepare_intervals/bed_files
      thread_count: freebayes_thread_count
      number_of_chunks: number_of_chunks_for_freebayes
      output_prefix:
        source: prepare_intervals/bed_files
        valueFrom: $(self.nameroot)
    out: [time_metrics_from_freebayes,
          time_metrics_from_picard_sortvcf,
          time_metrics_from_selectvariants,
          freebayes_vcf]

  sort_gatk4:
    run: ./tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: gatk4_cohort_genotyping/gatk4_cohort_genotyping_vcf
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        source: job_uuid
        valueFrom: $('genomel_cohort.gatk4.genomel_all.' + self)
    out: [sorted_vcf, time_metrics]

  sort_freebayes:
    run: ./tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf: freebayes_cohort_genotyping/freebayes_vcf
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        source: job_uuid
        valueFrom: $('genomel_cohort.freebayes.genomel_all.' + self)
    out: [sorted_vcf, time_metrics]

  variant_ensemble:
    run: ./tools/variant_calling/bcbio_variant_ensemble.cwl
    in:
      job_uuid: job_uuid
      config_json: config_json
      reference: reference
      output_name:
        source: job_uuid
        valueFrom: $(self + 'variant_ensemble.vcf.gz')
      input_vcf: [sort_gatk4/sorted_vcf, sort_freebayes/sorted_vcf]
    out: [ensemble_vcf, time_metrics]

  sort_ensemble:
    run: ./tools/variant_calling/picard_sortvcf.cwl
    in:
      job_uuid: job_uuid
      vcf:
        source: variant_ensemble/ensemble_vcf
        valueFrom: $([self])
      reference_dict:
        source: reference
        valueFrom: $(self.secondaryFiles[1])
      output_prefix:
        source: job_uuid
        valueFrom: $('genomel_cohort.variant_ensemble.genomel_all.' + self)
    out: [sorted_vcf, time_metrics]

  upload_gatk4_vcf:
    run: ./tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input: sort_gatk4/sorted_vcf
      s3uri:
        source: [upload_s3_bucket, job_uuid, sort_gatk4/sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  upload_gatk4_vcf_index:
    run: ./tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input:
        source: sort_gatk4/sorted_vcf
        valueFrom: $(self.secondaryFiles[0])
      s3uri:
        source: [upload_s3_bucket, job_uuid, sort_gatk4/sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].secondaryFiles[0].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  upload_freebayes_vcf:
    run: ./tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input: sort_freebayes/sorted_vcf
      s3uri:
        source: [upload_s3_bucket, job_uuid, sort_freebayes/sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  upload_freebayes_vcf_index:
    run: ./tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input:
        source: sort_freebayes/sorted_vcf
        valueFrom: $(self.secondaryFiles[0])
      s3uri:
        source: [upload_s3_bucket, job_uuid, sort_freebayes/sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].secondaryFiles[0].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  upload_ensemble_vcf:
    run: ./tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input: sort_ensemble/sorted_vcf
      s3uri:
        source: [upload_s3_bucket, job_uuid, sort_ensemble/sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  upload_ensemble_vcf_index:
    run: ./tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input:
        source: sort_ensemble/sorted_vcf
        valueFrom: $(self.secondaryFiles[0])
      s3uri:
        source: [upload_s3_bucket, job_uuid, sort_ensemble/sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].secondaryFiles[0].basename)
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
    out: [output, time_metrics]

  extract_time_log:
    run: ./tools/utils/extract_outputs.cwl
    in:
      file_array:
        source: [gatk4_cohort_genotyping/time_metrics_from_gatk4_cohort_genotyping,
                 gatk4_cohort_genotyping/time_metrics_from_picard_sortvcf,
                 gatk4_cohort_genotyping/time_metrics_from_selectvariants,
                 freebayes_cohort_genotyping/time_metrics_from_freebayes,
                 freebayes_cohort_genotyping/time_metrics_from_picard_sortvcf,
                 freebayes_cohort_genotyping/time_metrics_from_selectvariants,
                 variant_ensemble/time_metrics,
                 sort_gatk4/time_metrics,
                 sort_freebayes/time_metrics,
                 sort_ensemble/time_metrics,
                 upload_gatk4_vcf/time_metrics,
                 upload_gatk4_vcf_index/time_metrics,
                 upload_freebayes_vcf/time_metrics,
                 upload_freebayes_vcf_index/time_metrics,
                 upload_ensemble_vcf/time_metrics,
                 upload_ensemble_vcf_index/time_metrics]
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
