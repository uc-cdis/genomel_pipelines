#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: ScatterFeatureRequirement

inputs:
  aws_config: File
  aws_shared_credentials: File
  s3_profile: string
  s3_endpoint: string
  bam: File
  bam_uri: string
  bam_index: File
  bam_index_uri: string
  gvcf: File
  gvcf_uri: string
  gvcf_index: File
  gvcf_index_uri: string

outputs:
  time_metrics_from_upload_bam:
    type: File
    outputSource: upload_bam/time_metrics
  time_metrics_from_upload_bam_index:
    type: File
    outputSource: upload_bam_index/time_metrics
  time_metrics_from_upload_gvcf:
    type: File
    outputSource: upload_gvcf/time_metrics
  time_metrics_from_upload_gvcf_index:
    type: File
    outputSource: upload_gvcf_index/time_metrics

steps:
  upload_bam:
    run: ../../tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
      input: bam
      s3uri: bam_uri
    out: [output, time_metrics]

  upload_bam_index:
    run: ../../tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
      input: bam_index
      s3uri: bam_index_uri
    out: [output, time_metrics]

  upload_gvcf:
    run: ../../tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
      input: gvcf
      s3uri: gvcf_uri
    out: [output, time_metrics]

  upload_gvcf_index:
    run: ../../tools/utils/awscli_upload.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
      input: gvcf_index
      s3uri: gvcf_index_uri
    out: [output, time_metrics]
