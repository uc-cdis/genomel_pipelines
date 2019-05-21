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
    input_vcf: File
    gwascat: File
    config: File

outputs:
    gwascat_annotated_vcf:
        type: File
        outputBinding:
            glob: "*.gwascat.vcf"
    time_metrics:
        type: File
        outputBinding:
            glob: "*.gwascat.time.json"

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.gwascat.time.json')
        java -Xmx16G -jar /opt/SnpSift.jar gwasCat -c $(inputs.config.path) -db $(inputs.gwascat.path) $(inputs.input_vcf.path) > $(inputs.input_vcf.nameroot).gwascat.vcf
