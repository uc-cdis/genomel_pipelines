#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  aws_config: File
  aws_shared_credentials: File
  s3_profile: string
  s3_endpoint: string
  bam_url: string
  bam_md5: string
  aliquot_id: string
  job_uuid: string
  upload_bam_url: string

outputs:
  reheadered_bam:
    type: File
    outputSource: samtools_index/bam_with_index
  time_metrics:
    type: File
    outputSource: replace_readgroup/time_metrics

steps:
  download_bam:
    run: ./download_check.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
      s3uri: bam_url
      md5: bam_md5
    out: [verified_file, time_metrics_from_download]

  get_bam_header:
    run: ../../tools/harmonization/get_bam_header.cwl
    in:
      bam: download_bam/verified_file
    out: [bam_header]

  replace_readgroup:
    run: ../../tools/harmonization/readgroup_replace.cwl
    in:
      old_header: get_bam_header/bam_header
      aliquot_id: aliquot_id
      input_bam: download_bam/verified_file
      job_uuid: job_uuid
    out: [rg_fixed_bam, time_metrics]

  samtools_index:
    run: ../../tools/harmonization/samtools_index.cwl
    in:
      input_bam_path: replace_readgroup/rg_fixed_bam
    out: [bam_with_index]

  upload_reheadered_bam:
    run: ../../tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input: replace_readgroup/rg_fixed_bam
      s3uri: upload_bam_url
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [output, time_metrics]

  upload_reheadered_bam_index:
    run: ../../tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      input:
        source: samtools_index/bam_with_index
        valueFrom: $(self.secondaryFiles[0])
      s3uri:
        source: upload_bam_url
        valueFrom: $(self.replace(".bam", ".bai"))
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [output, time_metrics]
