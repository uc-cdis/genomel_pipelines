#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/gatk4_0_11:2.0
  - class: InitialWorkDirRequirement
    listing:
      - entryname: "gvcf_path.list"
        entry: |
          ${
            var paths = [];
            for (var i = 0; i < inputs.gvcf_files.length; i++){
              if (inputs.gvcf_files[i]["nameext"] == ".gz"){
                paths.push(inputs.gvcf_files[i]["path"])
                }
              }
            return paths.join("\n")
            }
  - class: ResourceRequirement
    coresMin: 30

inputs:
  gvcf_files:
    type: File[]
    secondaryFiles: [.tbi]
  job_uuid: string
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  bed_file: File
  thread_count: int
  number_of_chunks: int
  cromwell_engine:
    type: boolean
    default: false
    inputBinding:
      position: 99
      prefix: -e

outputs:
  vcf_list:
    type: File[]
    outputBinding:
      glob: '*.vcf.gz'

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.genomel_pdc_gatk4_cohort_genotyping.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      sed 's/\\\\n/\\n/g' gvcf_path.list > fixed_gvcf_path.list

      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.genomel_pdc_gatk4_cohort_genotyping.time.json')
      python /opt/genomel_pdc_gatk4_cohort_genotyping.py
      --gvcf_path fixed_gvcf_path.list -j $(inputs.job_uuid) -f $(inputs.reference.path)
      -L $(inputs.bed_file.path) -n $(inputs.thread_count) -c $(inputs.number_of_chunks)
