
#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_novoalign_in_node_parallel:1.0

inputs:
  job_uuid: string
  nthreads:
    type: int
    default: 8
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
    type: File[]
    doc: Novoalign BAM output file.
    outputBinding:
      glob: '*.unsorted.bam'
  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.Novoalign_SamblasterDedup_' + inputs.nthreads + '_threads_each_readgroup' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.Novoalign_SamblasterDedup_' + inputs.nthreads + '_threads_each_readgroup' + '.time.json')
      python /opt/novoalign_dedup_multithreaded_by_readgroup.py
      -d $(inputs.dbname.path) -t $(inputs.nthreads)
