#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_novoalign:1.0

inputs:
  job_uuid: string
  dbname:
    type: File
    doc: Full pathname of indexed reference sequence created by novoindex.
  input_read1_fastq_file:
    type: File
    doc: FASTQ file for input read (read R1 in Paired End mode)
  input_read2_fastq_file:
    type: File
    doc: FASTQ file for read R2 in Paired End mode, if there is one.
  readgroup_line:
    type: string
    doc: Specifies the readgroup_line. (e.g. "@RG\tCN:\tPL:\tID:\tSM:\tPU:\tLB:")
  readgroup_name:
    type: string
    doc: Name of the output file.

outputs:
  readgroup_bam:
    type: File
    doc: Novoalign BAM output file.
    outputBinding:
      glob: '*bam'
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.Novoalign_' + inputs.readgroup_name + '_SamblasterDedup' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.Novoalign_' + inputs.readgroup_name + '_SamblasterDedup' + '.time.json')
      /opt/novocraft/novoalign
      -c 30
      -d $(inputs.dbname.path)
      -f $(inputs.input_read1_fastq_file.path) $(inputs.input_read2_fastq_file.path)
      -F STDFQ
      -i PE
      300,125
      -o SAM
      \"$(inputs.readgroup_line)\"
      | /opt/samblaster-v.0.1.24/samblaster -i /dev/stdin -o /dev/stdout
      | /opt/sambamba-0.6.8-linux-static view -t 30 -f bam -l 0 -S /dev/stdin
      | /opt/sambamba-0.6.8-linux-static sort -t 30 --natural-sort -m 15GiB --tmpdir ./
      -o $(inputs.readgroup_name).unsorted.bam -l 5 /dev/stdin
