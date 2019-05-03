#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/genomel_variant_calling:6.0
  - class: ResourceRequirement
    coresMin: 21

successCodes:
  - 0
  - 1

inputs:
  bam:
    type: File
    secondaryFiles: [^.bai]
  job_uuid: string
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  bed_file: File
  thread_count: int
  number_of_chunks: int

outputs:
  vcf_list:
    type: File[]
    outputBinding:
      glob: '*.vcf'

  bed_list:
    type: File[]
    outputBinding:
      glob: '*.bed'

  log_file:
    type: File
    outputBinding:
      glob: '*.pdc_freebayes_docker.log'

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.aws_freebayes.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.aws_freebayes.time.json')
      python /opt/aws_freebayes.py
      -b $(inputs.bam.path) -j $(inputs.job_uuid) -f $(inputs.reference.path)
      -t $(inputs.bed_file.path) -n $(inputs.thread_count) -c $(inputs.number_of_chunks)
