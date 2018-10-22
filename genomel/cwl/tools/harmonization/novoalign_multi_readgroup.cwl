#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization@sha256:2e2fe50befce7f34f80e54036e93aa195627eeba2256a83ee36f4e713f2f43ce

inputs:
  job_uuid: string
  nthreads:
    type: int
    default: 8
  concurrents:
    type: int
    default: 4
  dbname: File
  input_read1_fastq_files:
    type: File[]
    inputBinding:
      prefix: -f1
  input_read2_fastq_files:
    type: File[]
    inputBinding:
      prefix: -f2
  readgroup_lines:
    type: string[]
    inputBinding:
      prefix: -g
  readgroup_names:
    type: string[]
    inputBinding:
      prefix: -n

outputs:
  readgroup_bam:
    type: File
    doc: Novoalign BAM output file.
    outputBinding:
      glob: '*bam'
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.Novoalign_SamblasterDedup_' + inputs.nthreads + '_threads' + inputs.concurrents + '_concurrents' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.Novoalign_SamblasterDedup_' + inputs.nthreads + '_threads' + inputs.concurrents + '_concurrents' + '.time.json')
      /opt/novoalign_dedup_multithreaded_by_readgroup.py
      -d $(inputs.dbname.path) -t $(inputs.nthreads) -c $(inputs.concurrents)
