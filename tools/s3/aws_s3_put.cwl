#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool
requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/awscli:1
  - class: EnvVarRequirement
    envDef:
      - envName: "AWS_CONFIG_FILE"
        envValue: $(inputs.aws_config.path)
      - envName: "AWS_SHARED_CREDENTIALS_FILE"
        envValue: $(inputs.aws_shared_credentials.path)
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  - id: aws_config
    type: File
    doc: AWS S3 configuration file. Usually located at ~/.aws/config

  - id: aws_shared_credentials
    type: File
    doc: AWS S3 credentials file. Usually located at ~/.aws/credentials

  - id: input
    type: File
    doc: Local path for file to upload to S3
    inputBinding:
      position: 98

  - id: s3uri
    type: string
    doc: Remote path in S3 for the uploading file
    inputBinding:
      position: 99

  - id: s3_profile
    type: string
    doc: S3 profile associated to your bucket.
    inputBinding:
      position: 0
      prefix: --profile

  - id: s3_endpoint
    type: string
    doc: S3 endpoint associated to your bucket.
    inputBinding:
      position: 1
      prefix: --endpoint-url

outputs:
  - id: output
    type: File
    outputBinding:
      glob: "output"

arguments:
  - valueFrom: --no-verify-ssl
    position: 2
    
baseCommand: [aws, s3, cp]