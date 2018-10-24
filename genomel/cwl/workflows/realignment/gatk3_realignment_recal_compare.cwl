#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  job_uuid: string
  bam_path:
    type: File
    secondaryFiles: [^.bai]
  reference:
    type: File
    secondaryFiles: [.fai, ^.dict]
  known_indel:
    type: File
    secondaryFiles: [.tbi]
  known_snp:
    type: File
    secondaryFiles: [.tbi]

outputs:
  time_metrics_from_gatk3_leftalignindels:
    type: File
    outputSource: gatk3_leftalignindels/time_metrics
  time_metrics_from_gatk3_realignertargetcreator:
    type: File
    outputSource: gatk3_realignertargetcreator/time_metrics
  time_metrics_from_gatk3_indelrealigner:
    type: File
    outputSource: gatk3_indelrealigner/time_metrics
  time_metrics_from_gatk3_baserecalibrator_on_harmonized_bam:
    type: File
    outputSource: gatk3_baserecalibrator_on_harmonized_bam/time_metrics
  time_metrics_from_gatk3_baserecalibrator_on_realigned_bam:
    type: File
    outputSource: gatk3_baserecalibrator_on_realigned_bam/time_metrics
  time_metrics_from_gatk3_printreads_on_harmonized_bam:
    type: File
    outputSource: gatk3_printreads_on_harmonized_bam/time_metrics
  time_metrics_from_gatk3_printreads_on_realigned_bam:
    type: File
    outputSource: gatk3_printreads_on_realigned_bam/time_metrics
  harmonized_realigned_bam:
    type: File
    outputSource: gatk3_indelrealigner/realigned_bam
  harmonized_recal_bam:
    type: File
    outputSource: gatk3_printreads_on_harmonized_bam/recal_bam
  harmonized_realigned_recal_bam
    type: File
    outputSource: gatk3_printreads_on_realigned_bam/recal_bam

steps:
  gatk3_leftalignindels:
    run: ../../tools/realignment/gatk3_leftalignindels.cwl
    in:
      job_uuid: job_uuid
      bam_path: bam_path
      reference: reference
    out: [left_aligned_bam, time_metrics]

  gatk3_realignertargetcreator:
    run: ../../tools/realignment/gatk3_realigntargetcreator.cwl
    in:
      job_uuid: job_uuid
      bam_path: gatk3_leftalignindels/left_aligned_bam
      reference: reference
      known_indel: known_indel
      known_snp: known_snp
    out: [realigner_target, time_metrics]

  gatk3_indelrealigner:
    run: ../../tools/realignment/gatk3_indelrealigner.cwl
    in:
      job_uuid: job_uuid
      bam_path: gatk3_leftalignindels/left_aligned_bam
      reference: reference
      known_indel: known_indel
      known_snp: known_snp
      realigner_target: gatk3_realigntargetcreator/realigner_target
    out: [realigned_bam, time_metrics]

  gatk3_baserecalibrator_on_harmonized_bam:
    run: ../../tools/realignment/gatk3_baserecalibrator.cwl
    in:
      job_uuid:
        source: job_uuid
        valueFrom: $(self + '.on_harmonized_bam')
      bam_path: bam_path
      reference: reference
      known_snp: known_snp
    out: [recal_table, time_metrics]

  gatk3_baserecalibrator_on_realigned_bam:
    run: ../../tools/realignment/gatk3_baserecalibrator.cwl
    in:
      job_uuid:
        source: job_uuid
        valueFrom: $(self + '.on_realigned_bam')
      bam_path: gatk3_indelrealigner/realigned_bam
      reference: reference
      known_snp: known_snp
    out: [recal_table, time_metrics]

  gatk3_printreads_on_harmonized_bam:
    run: ../../tools/realignment/gatk3_printreads.cwl
    in:
      job_uuid:
        source: job_uuid
        valueFrom: $(self + '.on_harmonized_bam')
      bam_path: bam_path
      reference: reference
      recal_table: gatk3_baserecalibrator_on_harmonized_bam/recal_table
    out: [recal_bam, time_metrics]

  gatk3_printreads_on_realigned_bam:
    run: ../../tools/realignment/gatk3_printreads.cwl
    in:
      job_uuid:
        source: job_uuid
        valueFrom: $(self + '.on_realigned_bam')
      bam_path: gatk3_indelrealigner/realigned_bam
      reference: reference
      recal_table: gatk3_baserecalibrator_on_realigned_bam/recal_table
    out: [recal_bam, time_metrics]
