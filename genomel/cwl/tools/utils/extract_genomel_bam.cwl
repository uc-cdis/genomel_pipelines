#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

class: ExpressionTool

inputs:
  harmonized_bam: File
  harmonized_realigned_bam: File?

outputs:
  genomel_bam: File

expression: |
  ${
    var bam = [];
    if (inputs.harmonized_realigned_bam != null){
        bam.push(inputs.harmonized_realigned_bam)
      } else {
        bam.push(inputs.harmonized_bam)
      }
    };
    return {'genomel_bam': bam[0]};
  }
