#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: registry.gitlab.com/uc-cdis/genomel-primary-analysis/harmonization:1.0

inputs:
  - id: nthreads
    type: ["null", int]
    default: 4
    doc: Sets maximum number of threads to use. Defaults to one thread per CPU as reported by sysinfo(). This is usually the number of cores or twice the number of cores if hyper-threading is turned on. Lisenced version only. (e.g. 4)
    inputBinding:
      position: 1
      prefix: "-c"

  - id: dbname
    type: File
    doc: Full pathname of indexed reference sequence created by novoindex.
    inputBinding:
      position: 2
      prefix: "-d"

  - id: input_read1_fastq_file
    type: File
    doc: FASTQ file for input read (read R1 in Paired End mode)
    inputBinding:
      position: 3
      prefix: "-f"

  - id: input_read2_fastq_file
    type: ["null", File]
    doc: FASTQ file for read R2 in Paired End mode, if there is one.
    inputBinding:
      position: 4

  - id: format
    type: string
    doc: Specifies a read file format. For Fastq '_sequence.txt' files from Illumina Pipeline 1.3 please specify -F ILMFQ. Other values for the -F option could be found at novocraft website.
    inputBinding:
      position: 5
      prefix: "-F"

  - id: mode
    type: string
    doc: Sets mode. (e.g. PE)
    inputBinding:
      position: 6
      prefix: "-i"

  - id: length
    type: string
    doc: Sets approximate fragment length and standard deviation. (e.g. 300,125)
    inputBinding:
      position: 7

  - id: output_format
    type: string
    doc: Specifies the report format. (e.g. SAM)
    inputBinding:
      position: 8
      prefix: "-o"

  - id: readgroup
    type: string
    doc: Specifies the readgoup. (e.g. "@RG\tCN:\tPL:\tID:\tSM:\tPU:\tLB:")
    inputBinding:
      position: 9

  - id: reference_seq
    type: File
    doc: Reference fasta file, with .dict and .fai.
    inputBinding:
      position: 15
    secondaryFiles:
      - "^.dict"
      - ".fai"

  - id: output_name
    type: string
    doc: Name of the output file.

outputs:
- id: output_file
  type: File
  doc: Novoalign BAM output file.
  outputBinding:
    glob: $(inputs.output_name)

baseCommand: /opt/novocraft/novoalign
arguments:
  - valueFrom: "awk"
    position: 10
    prefix: "|"
  - valueFrom: "{if (($2 !~ /phiX174*/) && ($3 !~ /phiX174*/))  print}"
    position: 11

  - valueFrom: "samtools"
    position: 12
    prefix: "|"

  - valueFrom: "view"
    position: 13

  - valueFrom: "-bT"
    position: 14

  - valueFrom: '3'
    position: 16
    prefix: -f

  - valueFrom: "-"
    position: 17

  - valueFrom: $(inputs.output_name)
    position: 18
    prefix: ">"
