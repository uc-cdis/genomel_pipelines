#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization@sha256:2e2fe50befce7f34f80e54036e93aa195627eeba2256a83ee36f4e713f2f43ce
  - class: ShellCommandRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  new_header: File
  interval_bed: File
  bam: File

stdout: $(inputs.job_uuid + '.reheadered.bam')
outputs:
  reheadered_bam:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.reheadered.bam')

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.SamtoolsReheader' + '.time.json')

baseCommand: []
arguments:
  - shellQuote: False
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.SamtoolsFilter_Reheader' + '.time.json')
      samtools view -@ 32 -Shb -f 3 -L $(inputs.interval_bed.path) $(inputs.bam.path) -o $(inputs.bam.nameroot).filtered.bam
      && samtools reheader $(inputs.new_header.path) $(inputs.bam.nameroot).filtered.bam && rm $(inputs.bam.nameroot).filtered.bam
