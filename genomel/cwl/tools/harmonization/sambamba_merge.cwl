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

  bams:
    type: File[]
    inputBinding:
      position: 1
      shellQuote: false
      
  base_file_name: string

outputs:
  merged_bam:
    type: File
    outputBinding:
      glob: '*.bam'
      outputEval: |-
        ${
            if(inputs.bams.length > 1) return self
            else return inputs.bams
        }

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.SambambaMerge' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: |-
      ${
          var time_cmd = "/usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\" -o " + inputs.job_uuid + ".SambambaMerge" + ".time.json"
          if (inputs.bams.length != 1)
           return time_cmd + " /opt/sambamba-0.6.8-linux-static merge -t 32 " + inputs.base_file_name + ".aligned.duplicates_marked.unsorted.bam"
          else return time_cmd + " ls"
       }
