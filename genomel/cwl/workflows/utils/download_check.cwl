#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  aws_config: File
  aws_shared_credentials: File
  s3_profile: string
  s3_endpoint: string
  s3uri: string
  md5: string

outputs:
  verified_file:
    type: File?
    outputSource: checkmd5sum/output
  time_metrics_from_download:
    type: File
    outputSource: download/time_metrics

steps:
  download:
    run: ../../tools/utils/awscli_download.cwl
    in:
      aws_config: aws_config
      aws_shared_credentials: aws_shared_credentials
      s3uri: s3uri
      s3_profile: s3_profile
      s3_endpoint: s3_endpoint
    out: [output, time_metrics]

  checkmd5sum:
    run: ../../tools/utils/file_check.cwl
    in:
      file: download/output
      md5sum: md5
    out: [output]
