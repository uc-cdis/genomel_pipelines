#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/genomel_variant_calling:6.0

inputs:
  job_uuid: string
  input_vcf:
    type: File
    secondaryFiles: [.tbi]

  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]

  output_prefix: string

outputs:
  output_vcf:
    type: File
    outputBinding:
      glob: $(inputs.output_prefix + '.filtered.site_only.vcf.gz')
    secondaryFiles: [.tbi]

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.gatk3_selectvariants.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.gatk3_selectvariants.time.json')
      java -Xmx100G -XX:ParallelGCThreads=30 -jar /opt/GenomeAnalysisTK.jar
      -T SelectVariants --variant $(inputs.input_vcf.path)
      -R $(inputs.reference.path)
      -o $(inputs.output_prefix + '.filtered.site_only.vcf.gz')
      -select "QUAL > 20.0"
      -ef
      -env
