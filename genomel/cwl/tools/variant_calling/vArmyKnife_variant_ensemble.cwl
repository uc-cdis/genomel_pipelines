#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/yilinxu/variant-ensembl:vArmyKnife

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
  reference_dict: File

outputs:
  ensemble_vcf:
    type: File
    outputBinding:
      glob: $(inputs.output_name)
  sorted_vcf:
    type: File
    outputBinding:
      glob: $(inputs.output_name+ '.gz')
    secondaryFiles: [.tbi]
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.vArmyKnife_variant_ensemble.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.vArmyKnife_variant_ensemble.time.json')
      java -jar /opt/vArmyKnife.jar walkVcf
      --splitMultiAllelics
      --leftAlignAndTrim
      --genomeFA "$(inputs.reference.path)"
      --runEnsembleMerger
      --singleCallerVcfNames "gatk4,freebayes"
      --singleCallerPriority "gatk4,freebayes"
      --convertToStandardVcf
      "$(inputs.gatk4_vcf.path);$(inputs.freebayes_vcf.path)"
      "$(inputs.output_name)"
      java -jar /opt/picard.jar SortVcf CREATE_INDEX=true OUTPUT=$(inputs.job_uuid + "." + inputs.output_name + ".gz") SEQUENCE_DICTIONARY=$(inputs.reference_dict.path)
