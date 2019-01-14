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
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict,
                     .64.amb, .64.ann, .64.bwt, .64.pac, .64.sa,
                     .amb, .ann, .bwt, .pac, .sa]
  known_snp:
    type: File
    secondaryFiles: [.tbi]
  exome_bed: File
  ###Download
  aws_config: File
  aws_shared_credentials: File
  download_s3_profile: string
  download_s3_endpoint: string

  ###Alignment required
  input_is_fastq: int[]
  fastq_read1_uri: string[]
  fastq_read2_uri: string[]
  fastq_read1_md5: string[]
  fastq_read2_md5: string[]
  readgroup_lines: string[]
  readgroup_names: string[]

  ###Harmonization required
  input_is_bam: int[]
  bam_uri: string
  bam_md5: string

  ###Upload
  upload_s3_profile: string
  upload_s3_endpoint: string
  upload_s3_bucket: string

outputs:
  time_logs:
    type: File[]
    outputSource: extract_time_log/output
  genomel_bam:
    type: File
    outputSource: extract_genomel_bam/genomel_bam
  genomel_gvcf:
    type: File
    outputSource: gatk3_haplotypecaller/haplotypecaller_sorted_vcf

steps:
  download_fastq_reads:
    run: ./cwl/workflows/utils/download_fastq.cwl
    scatter: [input_is_fastq]
    in:
      input_is_fastq: input_is_fastq
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: download_s3_profile
      s3_endpoint: download_s3_endpoint
      fastq_read1_uri: fastq_read1_uri
      fastq_read2_uri: fastq_read2_uri
      fastq_read1_md5: fastq_read1_md5
      fastq_read2_md5: fastq_read2_md5
    out: [downloaded_fastq_read1,
          downloaded_fastq_read2,
          time_metrics_from_download_f1,
          time_metrics_from_download_f2]

  download_bam_file:
    run: ./cwl/workflows/utils/download_check.cwl
    scatter: [input_is_bam]
    in:
      input_is_bam: input_is_bam
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: bam_uri
      md5: bam_md5
      s3_profile: download_s3_profile
      s3_endpoint: download_s3_endpoint
    out: [verified_file, time_metrics_from_download]

  fastq_input_alignment_with_bwa:
    run: ./cwl/workflows/harmonization/alignment_bwa_mem_prod.cwl
    scatter: input_is_fastq
    in:
      input_is_fastq: input_is_fastq
      job_uuid: job_uuid
      input_read1:
        source: download_fastq_reads/downloaded_fastq_read1
        valueFrom: $(self[0])
      input_read2:
        source: download_fastq_reads/downloaded_fastq_read2
        valueFrom: $(self[0])
      readgroup_lines: readgroup_lines
      readgroup_names: readgroup_names
      reference: reference
    out: [sorted_bam,
          time_metrics_from_trim_adaptor,
          time_metrics_from_bwa_mem,
          time_metrics_from_merge,
          time_metrics_from_sort,
          time_metrics_from_mrkdup]

  bam_input_harmonization_with_bwa:
    run: ./cwl/workflows/harmonization/harmonization_bwa_mem_prod.cwl
    scatter: input_is_bam
    in:
      input_is_bam: input_is_bam
      job_uuid: job_uuid
      input_bam:
        source: download_bam_file/verified_file
        valueFrom: $(self[0])
      reference: reference
    out: [sorted_bam,
          time_metrics_from_bam_to_fastq,
          time_metrics_from_trim_adaptor,
          time_metrics_from_bwa_mem,
          time_metrics_from_merge,
          time_metrics_from_sort,
          time_metrics_from_mrkdup]

  extract_bam:
    run: ./cwl/tools/utils/extract_outputs.cwl
    in:
      file_array:
        source: [fastq_input_alignment_with_bwa/sorted_bam,
                 bam_input_harmonization_with_bwa/sorted_bam]
        valueFrom: $([self[0][0], self[1][0]])
    out: [output]

  extract_genomel_bam:
    run: ./cwl/tools/utils/extract_genomel_bam.cwl
    in:
      harmonized_bam:
        source: extract_bam/output
        valueFrom: $(self[0])
    out: [genomel_bam]

  gatk3_haplotypecaller:
    run: ./cwl/workflows/variant_calling/haplotypecaller.cwl
    in:
      job_uuid: job_uuid
      bam_file: extract_genomel_bam/genomel_bam
      reference: reference
      interval: exome_bed
      snp_ref: known_snp
    out: [haplotypecaller_sorted_vcf,
          time_metrics_from_gatk3_haplotypecaller,
          time_metrics_from_picard_sortvcf]

  upload_results:
    run: ./cwl/workflows/utils/upload_results.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: upload_s3_profile
      s3_endpoint: upload_s3_endpoint
      bam: extract_genomel_bam/genomel_bam
      bam_uri:
        source: [upload_s3_bucket, job_uuid, extract_genomel_bam/genomel_bam]
        valueFrom: $(self[0])/$(self[1])/$(self[2].basename)
      bam_index:
        source: extract_genomel_bam/genomel_bam
        valueFrom: $(self.secondaryFiles[0])
      bam_index_uri:
        source: [upload_s3_bucket, job_uuid, extract_genomel_bam/genomel_bam]
        valueFrom: $(self[0])/$(self[1])/$(self[2].secondaryFiles[0].basename)
      gvcf: gatk3_haplotypecaller/haplotypecaller_sorted_vcf
      gvcf_uri:
        source: [upload_s3_bucket, job_uuid, gatk3_haplotypecaller/haplotypecaller_sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].basename)
      gvcf_index:
        source: gatk3_haplotypecaller/haplotypecaller_sorted_vcf
        valueFrom: $(self.secondaryFiles[0])
      gvcf_index_uri:
        source: [upload_s3_bucket, job_uuid, gatk3_haplotypecaller/haplotypecaller_sorted_vcf]
        valueFrom: $(self[0])/$(self[1])/$(self[2].secondaryFiles[0].basename)
    out: [time_metrics_from_upload_bam,
          time_metrics_from_upload_bam_index,
          time_metrics_from_upload_gvcf,
          time_metrics_from_upload_gvcf_index]

  extract_time_log:
    run: ./cwl/tools/utils/extract_outputs.cwl
    in:
      file_array:
        source: [download_fastq_reads/time_metrics_from_download_f1,
                 download_fastq_reads/time_metrics_from_download_f2,
                 download_bam_file/time_metrics_from_download,
                 fastq_input_alignment_with_bwa/time_metrics_from_trim_adaptor,
                 fastq_input_alignment_with_bwa/time_metrics_from_bwa_mem,
                 fastq_input_alignment_with_bwa/time_metrics_from_merge,
                 fastq_input_alignment_with_bwa/time_metrics_from_sort,
                 fastq_input_alignment_with_bwa/time_metrics_from_mrkdup,
                 bam_input_harmonization_with_bwa/time_metrics_from_bam_to_fastq,
                 bam_input_harmonization_with_bwa/time_metrics_from_trim_adaptor,
                 bam_input_harmonization_with_bwa/time_metrics_from_bwa_mem,
                 bam_input_harmonization_with_bwa/time_metrics_from_merge,
                 bam_input_harmonization_with_bwa/time_metrics_from_sort,
                 bam_input_harmonization_with_bwa/time_metrics_from_mrkdup,
                 gatk3_haplotypecaller/time_metrics_from_gatk3_haplotypecaller,
                 gatk3_haplotypecaller/time_metrics_from_picard_sortvcf,
                 upload_results/time_metrics_from_upload_bam,
                 upload_results/time_metrics_from_upload_bam_index,
                 upload_results/time_metrics_from_upload_gvcf,
                 upload_results/time_metrics_from_upload_gvcf_index]
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
