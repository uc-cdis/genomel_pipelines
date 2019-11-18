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
        run: ./workflows/subworkflow_test.cwl
        in:
            input_bam: input_bam
        out: [ output_files ]

    test_scatter:
        run: ./tools/scatter_test.cwl
        scatter: file
        in:
            file: test_subworkflow/output_files
        out: [ output ]