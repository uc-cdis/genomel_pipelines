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
    reference:
        type: File
        secondaryFiles: [.fai, ^.dict]
    dbsnp_vcf:
        type: File
        secondaryFiles: [.tbi]
    mills_vcf:
        type: File
        secondaryFiles: [.idx]

outputs:
    gatk_annotated_vcf:
        type: File
        outputBinding:
            glob: "*.gatk_annotator.vcf"
    time_metrics:
        type: File
        outputBinding:
            glob: "*.gatk_annotator.time.json"

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.gatk_annotator.time.json')
        java -Xmx16G -jar /opt/GenomeAnalysisTK.jar -R $(inputs.reference.path) -T VariantAnnotator -U LENIENT_VCF_PROCESSING -D $(inputs.dbsnp_vcf.path) --comp:GOLD $(inputs.mills_vcf.path) --variant $(inputs.input_vcf.path) -L $(inputs.input_vcf.path) -o $(inputs.input_vcf.nameroot).gatk_annotator.vcf --disable_auto_index_creation_and_locking_when_reading_rods
