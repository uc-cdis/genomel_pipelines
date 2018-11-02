#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

class: ExpressionTool

inputs:
  harmonized_bam: File
  harmonized_realigned_bam: File[]?

outputs:
  genomel_bam: File

expression: |
  ${
    if (Array.isArray(inputs.harmonized_realigned_bam) && inputs.harmonized_realigned_bam.length == 1){
      var genomel_bam = inputs.harmonized_realigned_bam[0]
    } else {
      var genomel_bam = inputs.harmonized_bam
    }
    return {"genomel_bam": genomel_bam}
  }
