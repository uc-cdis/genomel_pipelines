import os

def get_meta(fb_log):
    meta_list = list()
    dct = dict()
    with open(fb_log, 'r') as fin:
        for line in fin:
            block = line.rstrip().split(': ')
            if len(block) == 3:
                dct[block[-2]] = block[-1]
                meta_list.append(dct)
    return meta_list

def get_pass_pair(dct):
    if dct.get('exitcode') and dct['exitcode'] == '0':
        cmd_block = dct['running'].split(' ')
        bed = os.path.basename(cmd_block[8])
        vcf = os.path.basename(cmd_block[10])
        return {bed: vcf}
    return None

