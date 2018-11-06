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
  ###Download
  aws_config: File
  aws_shared_credentials: File
  download_s3_profile: string
  download_s3_endpoint: string

  ###Alignment required
  input_is_fastq: int[]
  fastq_read1_uri: string[]
  fastq_read2_uri: string[]
  readgroup_lines: string[]
  readgroup_names: string[]

  ###Harmonization required
  input_is_bam: int[]
  bam_uri: string

  ###Realignment required
  run_gatk3_realignment: int[]
  known_indel1:
    type: File
    secondaryFiles: [.tbi]
  known_indel2:
    type: File
    secondaryFiles: [.tbi]

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
    run: ./cwl/workflows/utils/download_prep.cwl
    scatter: [input_is_fastq]
    in:
      input_is_fastq: input_is_fastq
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: download_s3_profile
      s3_endpoint: download_s3_endpoint
      fastq_read1_uri: fastq_read1_uri
      fastq_read2_uri: fastq_read2_uri
    out: [downloaded_fastq_read1,
          downloaded_fastq_read2,
          time_metrics_from_download_f1,
          time_metrics_from_download_f2]

  download_bam_file:
    run: ./cwl/tools/utils/awscli_download.cwl
    scatter: [input_is_bam]
    in:
      input_is_bam: input_is_bam
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: bam_uri
      s3_profile: download_s3_profile
      s3_endpoint: download_s3_endpoint
    out: [output, time_metrics]

  get_fai_bed:
    run: ./cwl/tools/harmonization/fai_to_bed.cwl
    in:
      ref_fai:
        source: reference
        valueFrom: $(self.secondaryFiles[0])
    out: [output_bed]

  fastq_input_alignment_with_bwa:
    run: ./cwl/workflows/harmonization/alignment_bwa_mem.cwl
    scatter: input_is_fastq
    in:
      input_is_fastq: input_is_fastq
      job_uuid: job_uuid
      interval_bed: get_fai_bed/output_bed
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
          time_metrics_from_bwa_mem_filter_dedup,
          time_metrics_from_merge,
          time_metrics_from_sort,
          time_metrics_from_reheader]

  bam_input_harmonization_with_bwa:
    run: ./cwl/workflows/harmonization/harmonization_bwa_mem.cwl
    scatter: input_is_bam
    in:
      input_is_bam: input_is_bam
      job_uuid: job_uuid
      interval_bed: get_fai_bed/output_bed
      input_bam:
        source: download_bam_file/output
        valueFrom: $(self[0])
      reference: reference
    out: [sorted_bam,
          time_metrics_from_bam_to_fastq,
          time_metrics_from_trim_adaptor,
          time_metrics_from_bwa_mem_filter_dedup,
          time_metrics_from_merge,
          time_metrics_from_sort,
          time_metrics_from_reheader]

  extract_bam:
    run: ./cwl/tools/utils/extract_outputs.cwl
    in:
      file_array:
        source: [fastq_input_alignment_with_bwa/sorted_bam,
                 bam_input_harmonization_with_bwa/sorted_bam]
        valueFrom: $([self[0][0], self[1][0]])
    out: [output]

  gatk3_realignment:
    run: ./cwl/workflows/realignment/gatk3_realignment.cwl
    scatter: run_gatk3_realignment
    in:
      run_gatk3_realignment: run_gatk3_realignment
      job_uuid: job_uuid
      bam_path:
        source: extract_bam/output
        valueFrom: $(self[0])
      reference: reference
      known_indel1: known_indel1
      known_indel2: known_indel2
    out: [harmonized_realigned_bam,
          time_metrics_from_gatk3_leftalignindels,
          time_metrics_from_gatk3_realignertargetcreator,
          time_metrics_from_gatk3_indelrealigner]

  extract_genomel_bam:
    run: ./cwl/tools/utils/extract_genomel_bam.cwl
    in:
      harmonized_bam:
        source: extract_bam/output
        valueFrom: $(self[0])
      harmonized_realigned_bam: gatk3_realignment/harmonized_realigned_bam
    out: [genomel_bam]

  gatk3_haplotypecaller:
    run: ./cwl/workflows/variant_calling/haplotypecaller.cwl
    in:
      job_uuid: job_uuid
      bam_file: extract_genomel_bam/genomel_bam
      reference: reference
      interval: get_fai_bed/output_bed
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
                 download_bam_file/time_metrics,
                 fastq_input_alignment_with_bwa/time_metrics_from_trim_adaptor,
                 fastq_input_alignment_with_bwa/time_metrics_from_bwa_mem_filter_dedup,
                 fastq_input_alignment_with_bwa/time_metrics_from_merge,
                 fastq_input_alignment_with_bwa/time_metrics_from_sort,
                 fastq_input_alignment_with_bwa/time_metrics_from_reheader,
                 bam_input_harmonization_with_bwa/time_metrics_from_bam_to_fastq,
                 bam_input_harmonization_with_bwa/time_metrics_from_trim_adaptor,
                 bam_input_harmonization_with_bwa/time_metrics_from_bwa_mem_filter_dedup,
                 bam_input_harmonization_with_bwa/time_metrics_from_merge,
                 bam_input_harmonization_with_bwa/time_metrics_from_sort,
                 bam_input_harmonization_with_bwa/time_metrics_from_reheader,
                 gatk3_realignment/time_metrics_from_gatk3_leftalignindels,
                 gatk3_realignment/time_metrics_from_gatk3_realignertargetcreator,
                 gatk3_realignment/time_metrics_from_gatk3_indelrealigner,
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
