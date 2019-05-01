#/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
    - class: ShellCommandRequirement
    - class: InlineJavascriptRequirement
    - class: InitialWorkDirRequirement
      listing:
       - entryname: $(inputs.outdir)
         entry: "$({class:'Directory',listing:[]})"
         writable: true
    - class: DockerRequirement
      dockerPull: quay.io/yilinxu/genomel-annotation:v1.0

inputs:
    job_uuid: string
    input_vcf:
        type: File
        secondaryFiles: [.tbi]
    chunk: int
    outdir:
        type: string

outputs:
    vcf_lists:
        type: File[]
        outputBinding:
            glob: $(inputs.outdir + "/*.vcf.gz")
        secondaryFiles: [.tbi]

    time_metrics:
        type: File
        outputBinding:
            glob: $(inputs.job_uuid + ".divide.time.json")

baseCommand: []
arguments:
    - position: 0
      shellQuote: false
      valueFrom: >-
        /usr/bin/time -f "{\\"real_time\\": \\"%E\\", \\"user_time\\": %U, \\"system_time\\": %S, \\"wall_clock\\": %e, \\"maximum_resident_set_size\\": %M, \\"average_total_mem\\": %K, \\"percent_of_cpu\\": \\"%P\\"}"
        -o $(inputs.job_uuid + '.divide.time.json')
        zcat $(inputs.input_vcf.path)| awk '\$1!~/^#/ {print}' > content.vcf &&
        zcat $(inputs.input_vcf.path)| awk '\$1~/^#/ {print}' > head.vcf &&
        split -a 4 -l $(inputs.chunk) content.vcf $(inputs.outdir)/$(inputs.input_vcf.nameroot). &&
        for f in $(inputs.outdir)/$(inputs.input_vcf.nameroot).????;do cat head.vcf $f >> $f.vcf && bgzip -c $f.vcf > $f.vcf.gz && tabix -p vcf $f.vcf.gz && rm $f $f.vcf; done
