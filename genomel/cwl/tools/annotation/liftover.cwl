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
    vcf_file: File
    reference:
        type: File
        secondaryFiles: [.fai, .amb, .ann, .bwt, .pac, .sa, ^.dict]
    chain: File

outputs:
    vcf_liftover:
        type: File
        outputBinding:
            glob: "*.liftover.vcf"
    vcf_reject:
        type: File
        outputBinding:
            glob: "*.reject.vcf"
    time_metrics:
        type: File
        outputBinding:
            glob: "*.liftover.time.json"

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.liftover.time.json')
        java -jar picard.jar LiftoverVcf \
        I=$(inputs.vcf_file.path) \
        O=$(inputs.vcf_file.basename.replace(".vcf","")).liftover.vcf
        CHAIN=$(inputs.chain.path) \
        REJECT=$(inputs.vcf_file.basename.replace(".vcf","")).reject.vcf
        R=$(inputs.reference.path)

