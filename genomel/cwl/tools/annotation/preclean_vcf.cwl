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

outputs:
    vcf_preclean:
        type: File
        outputBinding:
            glob: "*.vcf.gz"
        secondaryFiles: [.tbi]

    time_metrics:
        type: File
        outputBinding:
            glob: $(inputs.job_uuid + "preclean.time.json")

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
      -o $(inputs.job_uuid + '.preclean.time.json')
        vcftools
        --gzvcf $(inputs.vcf_file)
        --recode
        --recode-INFO ABHet
        --recode-INFO ABHom
        --recode-INFO set
        --out $(inputs.vcf_file.nameroot.replace("vcf",""))
      && awk '{if ($1~/^#/) {if ($1~/##INFO/) {if (($1~/ABHet/) || ($1~/ABHom/) || ($1~/set/)) print;} else print;} else print;}' $(inputs.vcf_file.nameroot.replace("vcf","")).recode.vcf > $(inputs.vcf_file.nameroot)
      && bgzip -c $(inputs.vcf_file.nameroot) > $(inputs.vcf_file)
      && tabix -p vcf $(inputs.vcf_file)
