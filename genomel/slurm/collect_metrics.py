import os
import glob
import pyslurm
import postgres.utils
import postgres.metrics

def get_prod_time():
    jobs = pyslurm.job()
    jdct = jobs.get()
    h = jdct[16478]['run_time']/float(3600)
    return h

def get_meta(fb_log):
    meta_list = list()
    wt_list = list()
    mrss_list = list()
    ec_list = list()
    with open(fb_log, 'r') as fin:
        for line in fin:
            block = line.rstrip().split(': ')
            if len(block) == 3:
                if 'wall_clock' in block[-2]:
                    wt_list.append(float(block[-1])/float(3600))
                elif 'maximum_resident_set_size' in block[-2]:
                    mrss_list.append(float(block[-1])/float(1024 ** 2))
                elif 'exitcode' in block[-2]:
                    ec_list.append(int(block[-1]))
    for i, j, k in zip(wt_list, mrss_list, ec_list):
        dct = {
            'wall_clock': float(),
            'maximum_resident_set_size': float(),
            'exitcode': int()
        }
        dct['wall_clock'] = i
        dct['maximum_resident_set_size'] = j
        dct['exitcode'] = k
        meta_list.append(dct)
    return meta_list

def sep_pass_fail(dct_list, wt_p, wt_f, mrss_p, mrss_f):
    for dct in dct_list:
        if dct['exitcode'] == 0:
            wt_p.append(dct['wall_clock'])
            mrss_p.append(dct['maximum_resident_set_size'])
        else:
            wt_f.append(dct['wall_clock'])
            mrss_f.append(dct['maximum_resident_set_size'])
    return wt_p, wt_f, mrss_p, mrss_f

def main():
    psql_conf = '/mnt/nfs/reference/postgres_config'
    psql_class = postgres.metrics.ProdMetrics
    logs = glob.glob('/mnt/nfs/cromwell_workdir/cromwell-executions/cwl_temp_file_2a169746-51ab-42bc-b7f0-458c8da66399.cwl/2a169746-51ab-42bc-b7f0-458c8da66399/call-freebayes_cohort_genotyping/shard-*/aws_freebayes.cwl/*/call-aws_freebayes/execution/675fda51-0918-4d3b-93ec-88192aa438ad.pdc_freebayes_docker.log')
    wt_p = list()
    wt_f = list()
    mrss_p = list()
    mrss_f = list()
    for log in logs:
        meta = get_meta(log)
        sep_pass_fail(meta, wt_p, wt_f, mrss_p, mrss_f)
    pg_data = {
        'prod_time': get_prod_time(),
        'nchunk_total': len(wt_p) + len(wt_f),
        'nchunk_passed': len(wt_p),
        'nchunk_failed': len(wt_f),
        'indiv_pass_time': wt_p,
        'indiv_fail_time': wt_f,
        'indiv_pass_mem': mrss_p,
        'indiv_fail_mem': mrss_f
    }
    engine = postgres.utils.get_db_engine(psql_conf)
    postgres.metrics.add_pfp_metrics(engine, psql_class, pg_data)

if __name__ == "__main__":
    main()