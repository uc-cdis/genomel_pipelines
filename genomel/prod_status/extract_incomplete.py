import os
import glob
# import argparse

def get_meta(fb_log):
    meta_list = list()
    cmd_list = list()
    ec_list = list()
    with open(fb_log, 'r') as fin:
        for line in fin:
            block = line.rstrip().split(': ')
            if len(block) == 3:
                if 'running' in block[-2]:
                    cmd_list.append(block[-1])
                elif 'exitcode' in block[-2]:
                    ec_list.append(block[-1])
    for i, j in zip(cmd_list, ec_list):
        dct = {
            'running': str(),
            'exitcode': str()
        }
        dct['running'] = i
        dct['exitcode'] = j
        meta_list.append(dct)
    return meta_list

def get_pass_pair(dct):
    if dct.get('exitcode') and dct['exitcode'] == '0':
        cmd_block = dct['running'].split(' ')
        bed = cmd_block[8]
        vcf = cmd_block[10]
        return {bed: vcf}
    return None

def get_list(lst):
    return [x for x in lst if x is not None]

# def create_hard_link(lst, key):
#     for i in lst:
#         check = os.path.basename(i)
#         if check == key:
#             os.link(i, key)

def main():
    '''main'''
    # parser = argparse.ArgumentParser('GenoMEL-PDC Freebayes extractor.')
    # # Required flags.
    # parser.add_argument('-l', \
    #                     '--log', \
    #                     required=True, \
    #                     action='append', \
    #                     help='Freebayes log file')
    # args = parser.parse_args()
    log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_2a169746-51ab-42bc-b7f0-458c8da66399.cwl/2a169746-51ab-42bc-b7f0-458c8da66399/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/675fda51-0918-4d3b-93ec-88192aa438ad.pdc_freebayes_docker.log')
    all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_2a169746-51ab-42bc-b7f0-458c8da66399.cwl/2a169746-51ab-42bc-b7f0-458c8da66399/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    pbed = list()
    pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.map'
    with open(pmap, 'w+') as of:
        for log in log_files:
            mdlist = get_meta(log)
            plist = get_list([get_pass_pair(x) for x in mdlist])
            for dct in plist:
                for k in dct.keys():
                    pbed.append('/mnt/nfs/cromwell_workdir{}'.format(k))
                for bed, vcf in dct.items():
                    of.writelines('{}\t{}\n'.format(bed, vcf))
    iclist = list(set(all_beds) - set(pbed))
    icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.map'
    with open(icmap, 'w+') as of:
        for i in iclist:
            of.writelines('{}\n'.format(i))
        # for dct in plist:
        #     for bed, vcf in dct.items():
        #         create_hard_link(bed_input, bed)
        #         create_hard_link(vcf_input, vcf)

if __name__ == "__main__":
    main()



