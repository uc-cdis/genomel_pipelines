#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_bwa:1.0

inputs:
  job_uuid: string
  reference:
    type: File
    secondaryFiles: [.fai, .64.amb, .64.ann, .64.bwt, .64.pac, .64.sa, ^.dict, .amb, .ann, .bwt, .pac, .sa]
  input_read1_fastq_file:
    type: File
    doc: FASTQ file for input read (read R1 in Paired End mode)
  input_read2_fastq_file:
    type: File
    doc: FASTQ file for read R2 in Paired End mode, if there is one.
  readgroup_line:
    type: string
    doc: Specifies the readgroup. (e.g. "@RG\tCN:\tPL:\tID:\tSM:\tPU:\tLB:")
  readgroup_name:
    type: string
    doc: Name of the output file.

outputs:
  readgroup_bam:
    type: File
    doc: BWA BAM output file.
    outputBinding:
      glob: '*bam'
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.BWA_mem_' + inputs.readgroup_name + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.BWA_mem_' + inputs.readgroup_name + '.time.json')
      /opt/bwa-0.7.17/bwa mem -K 100000000 -M -v 3 -t 30
      -Y $(inputs.reference.path) -R '$(inputs.readgroup_line)'
      $(inputs.input_read1_fastq_file.path) $(inputs.input_read2_fastq_file.path)
      | /opt/sambamba-0.6.8-linux-static view -t 30 -f bam -S -o $(inputs.readgroup_name).unsorted.bam /dev/stdin
