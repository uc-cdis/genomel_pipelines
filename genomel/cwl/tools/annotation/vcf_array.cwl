cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

class: ExpressionTool

inputs:
    vcf_file:
        type: File
    lines: int

outputs:
    vcf_array:
        type: File[]

expression: |
    ${
        var r = []
        if (inputs.lines ==1){
            r.push(inputs.vcf_file)
            }
        return {'vcf_array': r}
    }
