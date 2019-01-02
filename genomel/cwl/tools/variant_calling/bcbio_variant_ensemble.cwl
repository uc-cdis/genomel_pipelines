#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/variant-annotation:1.0

inputs:
  job_uuid: string
  config_json: File
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  output_name: string
  input_vcf:
    type: File[]
    secondaryFiles: [.tbi]
    inputBinding:
      position: 99
      shellQuote: false

outputs:
  ensemble_vcf:
    type: File
    outputBinding:
      glob: '*.vcf.gz'
    secondaryFiles: [.tbi]
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.bcbio_variant_ensemble.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.bcbio_variant_ensemble.time.json')
      java -Xmx100G -XX:ParallelGCThreads=30 -jar /opt/bcbio.variation-0.2.6-standalone.jar
      variant-ensemble $(inputs.config_json.path) $(inputs.reference.path) $(inputs.output_name)
