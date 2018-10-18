#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: ShellCommandRequirement
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization@sha256:2e2fe50befce7f34f80e54036e93aa195627eeba2256a83ee36f4e713f2f43ce

inputs:
  job_uuid: string

  bam: File

  base_file_name: string

  suffix:
    type: string
    default: aligned.duplicates_marked.sorted

outputs:
  sorted_bam:
    type: File
    outputBinding:
      glob: '*.bam'
    secondaryFiles: [^.bai]
    format: BAM

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.SambambaSort' + '.time.json')

baseCommand: []
arguments:
 - position: 0
   shellQuote: false
   valueFrom: >-
     /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
     -o $(inputs.job_uuid + '.SambambaSort' + '.time.json')
     /opt/sambamba-0.6.8-linux-static sort
     -t 32 -m 100G
     -o $(inputs.base_file_name).$(inputs.suffix).bam $(inputs.bam.path)
     && mv $(inputs.base_file_name).$(inputs.suffix).bam.bai $(inputs.base_file_name).$(inputs.suffix).bai
