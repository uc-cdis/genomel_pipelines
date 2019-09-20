from pysam import VariantFile
import pandas as pd
import requests
import json
import argparse
import flatten_json
from subprocess import call

categories = ["frameshift_insertion", "stopgain", "frameshift_deletion", "frameshift_substitution"]


def get_args():
    """Loads the parser"""
    parser = argparse.ArgumentParser(description="genomel qc")
    parser.add_argument('-vcf', '--vcffile', required=True, help="vcf file for filtering")
    parser.add_argument('-k', '--authfile', required=True, help="auth key file")
    parser.add_argument('-bam', '--bamfile', required=True, help="bam input csv")
    parser.add_argument('-fastq', '--fastqfile', required=True, help="fastq input csv")
    parser.add_argument('-case', '--casefile', required=False, help="case information csv")

    return parser.parse_args()


def add_keys(credential):
    '''
    Get auth from our secret keys
    '''
    global auth
    json_data = open(credential).read()
    keys = json.loads(json_data)
    auth = requests.post('https://genomel.bionimbus.org/user/credentials/cdis/access_token', json=keys)


def query_api(query_txt, variables=None):
    '''
    Request results for a specific query
    '''

    if variables == None:
        query = {'query': query_txt}
    else:
        query = {'query': query_txt, 'variables': variables}

    output = requests.post('https://genomel.bionimbus.org/api/v0/submission/graphql', headers={'Authorization': 'bearer ' + auth.json()['access_token']}, json=query).text
    data = json.loads(output)

    if 'errors' in data:
        print(data)

    return data


class Filter_vcf:
    """
    filter variant or sample for the vcf file
    """

    def __init__(self, vcf_file, categories, case_info_file):
        self.vcf_file = vcf_file
        self.categories = categories
        self.case_info_file = case_info_file

    """
    filter variant based on variant category and whether variant is deleterious
    """

    def filter_variant(self):
        vcf_in = VariantFile(self.vcf_file, "r")
        filter_variant = list()
        for rec in vcf_in.fetch():
            if "refGene_Exomic_Variant_Category" in rec.info.keys() and rec.info['refGene_Exomic_Variant_Category'][0] in self.categories:
                filter_variant.append(rec)
            elif "refGene_Exomic_Variant_Category" in rec.info.keys() and rec.info['refGene_Exomic_Variant_Category'][0] == "nonsynonymous_SNV":
                if ("dbNSFP_CADD_phred" in rec.info.keys() and float(rec.info['dbNSFP_CADD_phred'][0]) > 20) or ("dbNSFP_LRT_pred" in rec.info.keys() and rec.info['dbNSFP_LRT_pred'][0] == "D") or ("dbNSFP_MetaSVM_pred" in rec.info.keys() and rec.info['dbNSFP_MetaSVM_pred'][0] == "D") or ("dbNSFP_Polyphen2_HDIV_pred" in rec.info.keys() and rec.info['dbNSFP_Polyphen2_HDIV_pred'][0] == "D"):
                    if rec not in filter_variant:
                        filter_variant.append(rec)
        print("variant filtering: %s variants left" % len(filter_variant))
        return filter_variant

    """
    filter variant based on variant allele frequency (keep variant with AF<0.05)
    """

    def filter_freq(self, recs):
        invcf = VariantFile(self.vcf_file)
        outvcf = VariantFile('output.vcf', mode="w", header=invcf.header)
        filter_rec = list()
        for rec in recs:
            if "gnomAD_exomes_AF" in rec.info.keys() and rec.info['gnomAD_exomes_AF'][0] < 0.05:
                filter_rec.append(rec)
                outvcf.write(rec)
        print("Frequency filtering: %s variants left" % len(filter_rec))
        return filter_rec

    """
    Select samples having het or homo alt allel at the specific variants filter in the previous steps
    """

    def filter_sample(self, recs):
        filter_sample = list()
        for rec in recs:
            for key in rec.samples.keys():
                if rec.samples[key]['GT'] == (1, 1) and rec.samples[key]['GT_DISAGREE'] == ('0',) and key not in filter_sample:
                    filter_sample.append(key)
        print("Sample filtering: %s samples to be removed" % len(filter_sample))
        with open("sample_id.txt", "w") as fh:
            for item in filter_sample:
                fh.write(item)
                fh.write("\n")
        for command in ("~/Documents/Genomel/vcf_qc/bcftools/bcftools view -S sample_id.txt output.vcf > deleterious_varaint_remove_sample.vcf", "rm sample_id.txt", "rm output.vcf"):
            call(command, shell=True)
        return filter_sample

    """
    output a list of cases identified by previous criterial
    """

    def output_sample(self, filter_samples):
        case_info = pd.read_csv(self.case_info_file)
        sample_info = case_info[case_info['sample'].isin(filter_samples)]
        sample_info.to_csv("to_be_remove_sample.csv", index=None, header=True)


class Mapping_samples:
    """
    Identify case id, project, family id for samples that being called variants in the vcf_file
    """

    def __init__(self, vcf_file, bam_in, fastq_in):
        self.vcf_file = vcf_file
        self.bam_in = bam_in
        self.fastq_in = fastq_in

    """
    Identify case id and project based on sample name in vcf file
    """

    def retrieve_case(self):
        cases = list()
        vcf_in = VariantFile(self.vcf_file, "r")
        content = next(vcf_in.fetch())
        samples = content.samples.keys()
        bam_case = pd.read_csv(self.bam_in)
        bam_sample = list(map(lambda x: x.split('/')[-1], bam_case['s3_url']))
        base_bam = list(map(lambda x: x.strip('.bam'), bam_sample))
        bam_case['base_bam'] = base_bam
        fastq_case = pd.read_csv(self.fastq_in)
        for sample in samples:
            found = False
            if not fastq_case.loc[fastq_case['aliquot_id'] == sample].empty:
                content = fastq_case.loc[fastq_case['aliquot_id'] == sample].iloc[0]
                unaligned_reads_id = content["input_id_r1"]
                project = content["project"]
                add_info = self.retrive_addional_info("submitted_unaligned_reads", unaligned_reads_id)
                cases.append({"sample": sample, "unaligned_reads": unaligned_reads_id, "project": project, "aligned_reads": "", "case": add_info['case'], "family": add_info['family']})
            else:
                for index, row in bam_case.iterrows():
                    if sample in row['base_bam'] or row['base_bam'].strip() in sample:
                        found = True
                        aligned_reads_id = row['input_id']
                        project = row['project']
                        add_info = self.retrive_addional_info("submitted_aligned_reads", aligned_reads_id)
                        cases.append({"sample": sample, "unaligned_reads": "", "project": project, "aligned_reads": aligned_reads_id, "case": add_info['case'], "family": add_info['family']})
                        break
                if found:
                    found = False
                else:
                    cases.append({"sample": sample, "unaligned_reads": "", "project": "", "aligned_reads": "", "case": "", "family": ""})
        return cases

    """
    retrieve additional information from genomel data common api
    """

    def retrive_addional_info(self, type, id):
        query_txt = """{%s(id:"%s"){
            read_groups{
            aliquots{
                samples{
                    cases{
                        submitter_id
                        families{
                            submitter_id
                        }
                    }
                }
            }
            }
        }}""" % (type, id)

        data = query_api(query_txt)
        data = flatten_json.flatten_json(data)
        if type == "submitted_unaligned_reads":
            case = data['data_submitted_unaligned_reads_0_read_groups_0_aliquots_0_samples_0_cases_0_submitter_id']
            family = data['data_submitted_unaligned_reads_0_read_groups_0_aliquots_0_samples_0_cases_0_families_0_submitter_id']
        else:
            case = data['data_submitted_aligned_reads_0_read_groups_0_aliquots_0_samples_0_cases_0_submitter_id']
            family = data['data_submitted_aligned_reads_0_read_groups_0_aliquots_0_samples_0_cases_0_families_0_submitter_id']
        return {"case": case, "family": family}

    """
    write output case list into csv file
    """

    def output_file(self, cases):
        df = pd.DataFrame(cases)
        df.to_csv("vcf_case_mapping.csv", index=None, header=True)


if __name__ == "__main__":
    args = get_args()
    add_keys(args.authfile)
    if args.casefile:
        filter_obj = Filter_vcf(args.vcffile, categories, args.casefile)
    else:
        mapping_obj = Mapping_samples(args.vcffile, args.bamfile, args.fastqfile)
        cases = mapping_obj.retrieve_case()
        mapping_obj.output_file(cases)
        filter_obj = Filter_vcf(args.vcffile, categories, "vcf_case_mapping.csv")
    recs = filter_obj.filter_variant()
    filter_recs = filter_obj.filter_freq(recs)
    filter_sample = filter_obj.filter_sample(filter_recs)
    filter_obj.output_sample(filter_sample)
