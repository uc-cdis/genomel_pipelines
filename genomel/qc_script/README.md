## A list of python script to do QC for vcf file called by genomel WEX pipeline

### known_melanoma_risk_sample.py identify samples with known deleterious variant for 10 melanoma risk related genes, and those samples will potential be removed from downstream analysis from the vcf file.
Melanoma susceptible gene list: CDKN2A, CDK4, POT1, BAP1, TERT, MITF – 3:70014091 G>A only [rs149617956], ACD, TERF2IP
region.txt is the bed file for those 8 genes retrieved from UCSC genome browser. CDKN2A has 2 canonical transcripts.

### Input files:
    select_region.sort.vcf is the subset of sorted vcf file only have the regions with the melanoma susceptible gene

    credentials.json is the credential file download from genomel gen3 data common profile endpoint to make api call to genomel gen3 data common

    genomel_bam_input.csv and genomel_fastq_input.csv is the input file in postgres database prepared for running the genomel WEX pipeline.

### Run script:
    If no mapping file exist, the script will create the mapping file ("vcf_case_mapping.csv") to idenfy the samples in vcf with the case, family and project information in genomel gen3 common. The additional output will be "deleterious_varaint_remove_sample.vcf" and "to_be_remove_sample.csv"

    python3 known_melanoma_risk_sample.py -vcf select_region.sort.vcf -k credentials.json -bam genomel_bam_input.csv -fastq genomel_fastq_input.csv

    If the mapping file has be generated, the mapping file will be supplied in the script. The output will be "deleterious_varaint_remove_sample.vcf" and "to_be_remove_sample.csv"

    python3 known_melanoma_risk_sample.py -vcf select_region.sort.vcf -k credentials.json -bam genomel_bam_input.csv -fastq genomel_fastq_input.csv  -case vcf_case_mapping.csv



