#/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: InitialWorkDirRequirement
      listing:
        - $(inputs.snpeff_config)
        - $(inputs.annotation_directory)
    - class: ShellCommandRequirement
    - class: InlineJavascriptRequirement
    - class: DockerRequirement
      dockerPull: quay.io/yilinxu/genomel-annotation:v1.0

inputs:
    job_uuid: string
    snpeff_config: File
    input_vcf: File
    annotation_directory: Directory

outputs:
    snpeff_annotated_vcf:
        type: File
        outputBinding:
            glob: "*.snpeff.vcf"
    time_metrics:
        type: File
        outputBinding:
            glob: "*.snpeff.time.json"

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.snpeff.time.json')
        java -Xmx16G -jar /opt/snpEff.jar GRCh37.75 -c $(inputs.snpeff_config.basename) -v -stats -lof -motif -nextprot $(inputs.input_vcf.path) > $(inputs.input_vcf.nameroot).snpeff.vcf
