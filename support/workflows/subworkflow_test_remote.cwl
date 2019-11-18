#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
    input_bam: File
outputs:
    output_files:
        type: File[]
        outputSource: test_expr/output
steps:
    test_initworkdir:
        run: https://github.com/uc-cdis/genomel_pipelines/tree/benchmark/support/tools/initdir_test_remote.cwl
        in:
            input_bam: input_bam
        out: [ bam_with_index ]

    test_expr:
        run: https://github.com/uc-cdis/genomel_pipelines/tree/benchmark/support/tools/expressiontool_test_remote.cwl
        in:
            file_array:
                source: test_initworkdir/bam_with_index
                valueFrom: $([self, self.secondaryFiles[0]])
        out: [ output ]