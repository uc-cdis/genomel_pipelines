#/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: ShellCommandRequirement
    - class: InlineJavascriptRequirement
    - class: DockerRequirement
      dockerPull: quay.io/yilinxu/genomel-annotation:v1.0

inputs:
    job_uuid: string
    vcf_file:
        type: File
        secondaryFiles: [.tbi]

stdout: lines

outputs:
    chrm_vcf:
        type: File
        outputBinding:
            glob: "*chrm.vcf"
    no_chrm_vcf:
        type: File
        outputBinding:
            glob: "*chrm_no.vcf"
    lines:
        type: int
        outputBinding:
            glob: lines
            loadContents: true
            outputEval: |
                ${
                    var flag =1
                    if (self[0].contents.trim()=="0"){
                        flag = 0
                    }
                    return flag
                }

    time_metrics:
        type: File
        outputBinding:
            glob: $(inputs.job_uuid + ".split_chrm.time.json")

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.split_chrm.time.json')
        zcat $(inputs.vcf_file.path)| awk '\$1~/^chrM/ || \$1~/^MT/ {print}' > $(inputs.vcf_file.nameroot.replace("vcf",""))chrm.vcf &&
        zcat $(inputs.vcf_file.path)| awk '\$1!~/^chrM/ && \$1!~/^MT/ {print}' > $(inputs.vcf_file.nameroot.replace("vcf",""))chrm_no.vcf &&
        awk '\$1!~/^#/ {print}' $(inputs.vcf_file.nameroot.replace("vcf",""))chrm_no.vcf| wc -l
