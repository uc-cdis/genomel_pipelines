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
    # log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_2a169746-51ab-42bc-b7f0-458c8da66399.cwl/2a169746-51ab-42bc-b7f0-458c8da66399/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/675fda51-0918-4d3b-93ec-88192aa438ad.pdc_freebayes_docker.log')
    # log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_ed062ffc-2780-44a7-91b6-7efac8e39d5a.cwl/ed062ffc-2780-44a7-91b6-7efac8e39d5a/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/664fde8c-6d4e-428d-966a-9b5a9698ccbc.pdc_freebayes_docker.log')
    # log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_4a0adc5a-f55f-49f2-bcb4-c354dc0b7621.cwl/4a0adc5a-f55f-49f2-bcb4-c354dc0b7621/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/80e2ab48-c2b4-48f0-9473-5d7dab1cef06.pdc_freebayes_docker.log')
    # log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_4577c3f9-3698-44f2-9de5-6dcb5ccffb52.cwl/4577c3f9-3698-44f2-9de5-6dcb5ccffb52/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/f07235cd-131d-4c00-a80f-1a0f0a83c417.pdc_freebayes_docker.log')
    # log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_5f208e9a-b675-413c-ba67-bfc85c1ceed1.cwl/5f208e9a-b675-413c-ba67-bfc85c1ceed1/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/b214cafa-af0b-43ae-aced-b14a25c7a10e.pdc_freebayes_docker.log')
    log_files = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_082fee26-a07a-4bee-8a5a-f312e6d51677.cwl/082fee26-a07a-4bee-8a5a-f312e6d51677/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/a2d08426-7760-4f32-b85a-436570425d20.pdc_freebayes_docker.log')
    # all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_2a169746-51ab-42bc-b7f0-458c8da66399.cwl/2a169746-51ab-42bc-b7f0-458c8da66399/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    # all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_ed062ffc-2780-44a7-91b6-7efac8e39d5a.cwl/ed062ffc-2780-44a7-91b6-7efac8e39d5a/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    # all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_4a0adc5a-f55f-49f2-bcb4-c354dc0b7621.cwl/4a0adc5a-f55f-49f2-bcb4-c354dc0b7621/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    # all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_4577c3f9-3698-44f2-9de5-6dcb5ccffb52.cwl/4577c3f9-3698-44f2-9de5-6dcb5ccffb52/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    # all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_5f208e9a-b675-413c-ba67-bfc85c1ceed1.cwl/5f208e9a-b675-413c-ba67-bfc85c1ceed1/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    all_beds = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_082fee26-a07a-4bee-8a5a-f312e6d51677.cwl/082fee26-a07a-4bee-8a5a-f312e6d51677/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/*bed')
    pbed = list()
    # pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.map'
    # pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.2.map'
    # pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.3.map'
    # pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.4.map'
    # pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.5.map'
    pmap = '/mnt/nfs/cromwell_workdir/pass_bed_vcf.6.map'
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
    # icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.map'
    # icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.2.map'
    # icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.3.map'
    # icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.4.map'
    # icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.5.map'
    icmap = '/mnt/nfs/cromwell_workdir/incomplete_bed.6.map'
    with open(icmap, 'w+') as of:
        for i in iclist:
            of.writelines('{}\n'.format(i))
        # for dct in plist:
        #     for bed, vcf in dct.items():
        #         create_hard_link(bed_input, bed)
        #         create_hard_link(vcf_input, vcf)

if __name__ == "__main__":
    main()

