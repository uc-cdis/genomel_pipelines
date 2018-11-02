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
  fastq_read1_uri: string[]?
  fastq_read2_uri: string[]?
  bam_uri: string?
  input_is_fastq: int[]
  input_is_bam: int[]

outputs:
  downloaded_fastq_read1:
    type: File[]?
    outputSource: download_f1/output
  downloaded_fastq_read2:
    type: File[]?
    outputSource: download_f2/output
  downloaded_bam:
    type: File[]?
    outputSource: download_bam/output
  time_metrics_from_download_f1:
    type: File[]?
    outputSource: download_f1/time_metrics
  time_metrics_from_download_f2:
    type: File[]?
    outputSource: download_f2/time_metrics
  time_metrics_from_download_bam:
    type: File[]?
    outputSource: download_bam/time_metrics

steps:
  download_f1:
    run: ../../tools/utils/awscli_download.cwl
    scatter: [input_is_fastq, s3uri]
    scatterMethod: dotproduct
    in:
      input_is_fastq: input_is_fastq
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: fastq_read1_uri
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [output, time_metrics]

  download_f2:
    run: ../../tools/utils/awscli_download.cwl
    scatter: [input_is_fastq, s3uri]
    scatterMethod: dotproduct
    in:
      input_is_fastq: input_is_fastq
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: fastq_read2_uri
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [output, time_metrics]

  download_bam:
    run: ../../tools/utils/awscli_download.cwl
    scatter: [input_is_bam]
    in:
      input_is_bam: input_is_bam
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: bam_uri
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [output, time_metrics]
