#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/genomel_variant_calling:1.0

inputs:
  job_uuid: string
  gvcf_file:
    type: File[]
    inputBinding:
      prefix: -v
    secondaryFiles: [.tbi]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]

  interval: File
  snp_ref:
    type: File
    secondaryFiles: [.tbi]

outputs:
  vcf_list:
    type: File[]
    outputBinding:
      glob: '*.vcf.gz'
    secondaryFiles: [.tbi]
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.gatk3_genotypegvcfs.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.gatk3_genotypegvcfs.time.json')
      python /opt/gatk3_genotypegvcfs.py
      -j $(inputs.job_uuid) -r $(inputs.reference.path)
      -i $(inputs.interval.path) -s $(inputs.snp_ref.path) -c 25
