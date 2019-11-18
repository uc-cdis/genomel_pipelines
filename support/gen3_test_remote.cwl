#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement
  - class: SchemaDefRequirement
    types:
      - $import: capture_kit.yml

inputs:
    input_bam: File
    capture_kit: capture_kit.yml#capture_kit
outputs:
    output:
        type: string[]
        outputSource: test_scatter/output

steps:
    test_subworkflow:
        run: https://github.com/uc-cdis/genomel_pipelines/tree/benchmark/support/workflows/subworkflow_test_remote.cwl
        in:
            input_bam: input_bam
        out: [ output_files ]

    test_scatter:
        run: https://github.com/uc-cdis/genomel_pipelines/tree/benchmark/support/tools/scatter_test_remote.cwl
        scatter: file
        in:
            file: test_subworkflow/output_files
        out: [ output ]