#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization_with_bwa:1.0
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
  - class: ShellCommandRequirement

class: CommandLineTool

inputs:
  job_uuid: string

  readgroup_lines: string[]

  readgroup_names: string[]

  collate:
    type: int
    default: 1
  filename:
    type: File
  gz:
    type: int
    default: 1
  inputformat:
    type: string
    default: "bam"
  level:
    type: int
    default: 5
  outputdir:
    type: string
    default: .
  outputperreadgroup:
    type: int
    default: 1
  outputperreadgrouprgsm:
    type: int
    default: 1
  outputperreadgroupsuffixF:
    type: string
    default: _1.fq.gz
  outputperreadgroupsuffixF2:
    type: string
    default: _2.fq.gz
  outputperreadgroupsuffixO:
    type: string
    default: _o1.fq.gz
  outputperreadgroupsuffixO2:
    type: string
    default: _o2.fq.gz
  outputperreadgroupsuffixS:
    type: string
    default: _s.fq.gz
  tryoq:
    type: int
    default: 1
  T:
    type: string
    default: tempfq

outputs:
  output_readgroup_lines:
    type: string[]
    outputBinding:
      outputEval: |
        ${ return inputs.readgroup_lines.sort(function(a,b) { return a > b ? 1 : (a < b ? -1 : 0) }) }

  output_readgroup_names:
    type: string[]
    outputBinding:
      outputEval: |
        ${ return inputs.readgroup_names.sort(function(a,b) { return a > b ? 1 : (a < b ? -1 : 0) }) }

  output_fastq1:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*_1.fq.gz"
      outputEval: |
        ${ return self.sort(function(a,b) { return a.location > b.location ? 1 : (a.location < b.location ? -1 : 0) }) }

  output_fastq2:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*_2.fq.gz"
      outputEval: |
        ${ return self.sort(function(a,b) { return a.location > b.location ? 1 : (a.location < b.location ? -1 : 0) }) }

  time_metrics:
    type: File
    outputBinding:
      glob: $(inputs.job_uuid + '.SamtoolsViewBam_BammToFastq' + '.time.json')

baseCommand: []
arguments:
  - position: 0
    shellQuote: false
    valueFrom: >-
      /usr/bin/time -f \"{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"average_total_mem\": %K, \"percent_of_cpu\": \"%P\"}\"
      -o $(inputs.job_uuid + '.SamtoolsViewBam_BammToFastq' + '.time.json')
      samtools view -@ 8 -Shb $(inputs.filename.path)
      | /opt/biobambam2/2.0.87-release-20180301132713/x86_64-etch-linux-gnu/bin/bamtofastq
      collate=$(inputs.collate)
      filename=/dev/stdin
      gz=$(inputs.gz)
      inputformat=$(inputs.inputformat)
      level=$(inputs.level)
      outputdir=$(inputs.outputdir)
      outputperreadgroup=$(inputs.outputperreadgroup)
      outputperreadgrouprgsm=$(inputs.outputperreadgrouprgsm)
      outputperreadgroupsuffixF=$(inputs.outputperreadgroupsuffixF)
      outputperreadgroupsuffixF2=$(inputs.outputperreadgroupsuffixF2)
      outputperreadgroupsuffixO=$(inputs.outputperreadgroupsuffixO)
      outputperreadgroupsuffixO2=$(inputs.outputperreadgroupsuffixO2)
      outputperreadgroupsuffixS=$(inputs.outputperreadgroupsuffixS)
      tryoq=$(inputs.tryoq)
      T=$(inputs.T)
