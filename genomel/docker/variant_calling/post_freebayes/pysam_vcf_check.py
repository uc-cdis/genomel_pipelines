import pysam
import sys

def vcf_record_count(vcf):
    v = pysam.VariantFile(vcf)
    print(len(list(v.fetch())))

if __name__ == "__main__":
    vcf_record_count(sys.argv[1])
