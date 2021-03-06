#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-secondary-analysis/gatk3.7-0-gcfedb67:1.0

inputs:
  job_uuid: string
  bam_path:
    type: File
    secondaryFiles: [^.bai]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  known_snp:
    type: File
    secondaryFiles: [.tbi]

outputs:
  recal_table:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.recal_data.table')

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.gatk3_baserecalibrator.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.gatk3_baserecalibrator.time.json')
      java -Xmx100G -jar /opt/GenomeAnalysisTK.jar -T BaseRecalibrator
      -nct 30
      -I $(inputs.bam_path.path)
      -R $(inputs.reference.path)
      -knownSites $(inputs.known_snp.path)
      -o $(inputs.job_uuid + '.recal_data.table')
