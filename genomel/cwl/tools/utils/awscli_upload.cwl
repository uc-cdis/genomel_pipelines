#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool
requirements:
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-tools/awscli:1.0
  - class: EnvVarRequirement
    envDef:
      - envName: "AWS_CONFIG_FILE"
        envValue: $(inputs.aws_config.path)
      - envName: "AWS_SHARED_CREDENTIALS_FILE"
        envValue: $(inputs.aws_shared_credentials.path)
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement

inputs:
  aws_config: File

  aws_shared_credentials: File

  input: File

  s3uri: string

  s3_profile: string

  s3_endpoint: string

outputs:
  output:
    type: File
    outputBinding:
      glob: "output"

  time_metrics:
    type: File
    outputBinding:
      glob: $('aws_upload.' + inputs.input.basename + '.time.json')

baseCommand: []
stdout: output
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $('aws_upload.' + inputs.input.basename + '.time.json')
      aws --profile $(inputs.s3_profile) --endpoint-url $(inputs.s3_endpoint)
      --no-verify-ssl s3 cp $(inputs.input.path) $(inputs.s3uri)
