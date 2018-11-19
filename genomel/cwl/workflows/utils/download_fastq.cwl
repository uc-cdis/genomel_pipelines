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
  aws_config: File
  aws_shared_credentials: File
  s3_profile: string
  s3_endpoint: string
  fastq_read1_uri: string[]
  fastq_read2_uri: string[]
  fastq_read1_md5: string[]
  fastq_read2_md5: string[]

outputs:
  downloaded_fastq_read1:
    type: File[]
    outputSource: download_f1/verified_file
  downloaded_fastq_read2:
    type: File[]
    outputSource: download_f2/verified_file
  time_metrics_from_download_f1:
    type: File[]
    outputSource: download_f1/time_metrics_from_download
  time_metrics_from_download_f2:
    type: File[]
    outputSource: download_f2/time_metrics_from_download

steps:
  download_f1:
    run: ./download_check.cwl
    scatter: [s3uri, md5]
    scatterMethod: dotproduct
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: fastq_read1_uri
      md5: fastq_read1_md5
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [verified_file, time_metrics_from_download]

  download_f2:
    run: ./download_check.cwl
    scatter: [s3uri, md5]
    scatterMethod: dotproduct
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: fastq_read2_uri
      md5: fastq_read2_md5
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [verified_file, time_metrics_from_download]
