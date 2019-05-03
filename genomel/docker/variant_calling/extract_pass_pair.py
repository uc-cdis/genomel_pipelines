import os
import argparse

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
        bed = os.path.basename(cmd_block[8])
        vcf = os.path.basename(cmd_block[10])
        return {bed: vcf}
    return None

def get_list(lst):
    return [x for x in lst if x is not None]

def create_hard_link(lst, key):
    for i in lst:
        check = os.path.basename(i)
        if check == key:
            os.link(i, key)

def main():
    '''main'''
    parser = argparse.ArgumentParser('GenoMEL-PDC Freebayes extractor.')
    # Required flags.
    parser.add_argument('-b', \
                        '--bed', \
                        required=True, \
                        action='append')
    parser.add_argument('-v', \
                        '--vcf', \
                        required=True, \
                        action='append')
    parser.add_argument('-l', \
                        '--log', \
                        required=True, \
                        help='Freebayes log file')
    args = parser.parse_args()
    bed_input = args.bed
    vcf_input = args.vcf
    log_file = args.log
    mdlist = get_meta(log_file)
    plist = get_list([get_pass_pair(x) for x in mdlist])
    for dct in plist:
        for bed, vcf in dct.items():
            create_hard_link(bed_input, bed)
            create_hard_link(vcf_input, vcf)

if __name__ == "__main__":
    main()



