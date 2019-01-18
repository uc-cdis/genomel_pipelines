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
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  output_name: string
  gatk4_vcf:
    type: File
    secondaryFiles: [.tbi]
  freebayes_vcf:
    type: File
    secondaryFiles: [.tbi]

outputs:
  ensemble_vcf:
    type: File
    outputBinding:
      glob: $(inputs.output_name)
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
      /opt/bcbio.variation.recall-0.1.9/bin/bcbio-variation-recall -Xmx100G
      ensemble -n 1 --names gatk4,freebayes -c 20 $(inputs.output_name)
      $(inputs.reference.path) $(inputs.gatk4_vcf.path) $(inputs.freebayes_vcf.path)
