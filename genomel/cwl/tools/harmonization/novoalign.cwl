#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization:1.0

inputs:
  job_uuid: string
  nthreads:
    type: int
    default: 32
    doc: Sets maximum number of threads to use. Defaults to one thread per CPU as reported by sysinfo(). This is usually the number of cores or twice the number of cores if hyper-threading is turned on. Lisenced version only. (e.g. 4)
  dbname:
    type: File
    doc: Full pathname of indexed reference sequence created by novoindex.
  input_read1_fastq_file:
    type: File
    doc: FASTQ file for input read (read R1 in Paired End mode)
  input_read2_fastq_file:
    type: File
    doc: FASTQ file for read R2 in Paired End mode, if there is one.
  readgroup:
    type: string
    doc: Specifies the readgroup. (e.g. "@RG\tCN:\tPL:\tID:\tSM:\tPU:\tLB:")
  output_name:
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
      glob: $(inputs.job_uuid + '.Novoalign_' + inputs.output_name + '_SamblasterDedup_' + inputs.nthreads + '_threads' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.Novoalign_' + inputs.output_name + '_SamblasterDedup_' + inputs.nthreads + '_threads' + '.time.json')
      /opt/novocraft/novoalign
      -c $(inputs.nthreads)
      -d $(inputs.dbname.path)
      -f $(inputs.input_read1_fastq_file.path) $(inputs.input_read2_fastq_file.path)
      -F STDFQ
      -i PE
      300,125
      -o SAM
      \"$(inputs.readgroup)\"
      | /opt/samblaster-v.0.1.24/samblaster -i /dev/stdin -o /dev/stdout
      | /opt/sambamba-0.6.8-linux-static view -t $(inputs.nthreads) -f bam -l 0 -S /dev/stdin
      | /opt/sambamba-0.6.8-linux-static sort -t $(inputs.nthreads) --natural-sort -m 15GiB --tmpdir ./
      -o $(inputs.output_name).unsorted.bam -l 5 /dev/stdin
