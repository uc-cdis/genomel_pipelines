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
    if (inputs.harmonized_realigned_bam[0] != null){
        return {"genomel_bam": inputs.harmonized_realigned_bam[0]}
      } else {
        return {"genomel_bam": inputs.harmonized_bam}
      }
    }
  }
