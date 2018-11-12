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
  vcf:
    type:
      type: array
      items: File
      inputBinding:
        prefix: I=
        separate: false
    secondaryFiles: [.tbi]
  reference_dict: File
  output_prefix: string

outputs:
  sorted_vcf:
    type: File
    outputBinding:
      glob: '*.vcf.gz'
    secondaryFiles: [.tbi]
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.picard_sortvcf.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.picard_sortvcf.time.json')
      java -Xmx100G -XX:ParallelGCThreads=30 -jar /opt/picard.jar
      SortVcf CREATE_INDEX=true OUTPUT=$(inputs.job_uuid + '.' + inputs.output_prefix + '.vcf.gz')
      SEQUENCE_DICTIONARY=$(inputs.reference_dict.path)
