#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-exome-variant-detection/genomel_variant_calling:3.0
  - class: InitialWorkDirRequirement
    listing:
      - entryname: "bam_path.list"
        entry: |
          ${
            var paths = [];
            for (var i = 0; i < inputs.bam_files.length; i++){
              if (inputs.bam_files[i]["nameext"] == ".bam"){
                paths.push(inputs.bam_files[i]["path"])
                }
              }
            return paths.join("\n")
            }
  - class: ResourceRequirement
    coresMin: 30

inputs:
  bam_files:
    type: File[]
    secondaryFiles: [^.bai]
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
      glob: '*.vcf'

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.genomel_pdc_freebayes.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      sed 's/\\\\n/\\n/g' bam_path.list > fixed_bam_path.list

      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.genomel_pdc_freebayes.time.json')
      python /opt/genomel_pdc_freebayes.py
      -L fixed_bam_path.list -j $(inputs.job_uuid) -f $(inputs.reference.path)
      -t $(inputs.bed_file.path) -n $(inputs.thread_count) -c $(inputs.number_of_chunks)
