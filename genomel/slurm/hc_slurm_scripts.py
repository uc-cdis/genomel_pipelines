import postgres.status
import postgres.utils
import uuid
import argparse
import os

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Haplotype caller workflow SLURM script creator")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--thread_count", help="Thread count", required=True)
    required.add_argument('--java_heap', help='Java heap mem', required=True)
    required.add_argument("--mem", help="Max mem for each node", required=True)
    required.add_argument("--refdir", help="Reference dir on node", required=True)
    required.add_argument("--s3dir", help="S3bin for uploading output files", required=True)
    required.add_argument("--postgres_config", help="Path to postgres config file", required=True)
    required.add_argument("--outdir", default="./", help="Output directory for slurm scripts")
    required.add_argument("--status_table", default="None", help="Postgres status table name")
    required.add_argument("--s3_profile", help="S3 profile")    
    required.add_argument("--s3_endpoint", help="S3 endpoint")  


    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: %s" %args.outdir)

    if not os.path.isfile(args.postgres_config):
        raise Exception("Cannot find config file: %s" %args.postgres_config)

    engine = postgres.utils.get_db_engine(args.postgres_config)
    cases = postgres.status.get_case_from_status(engine, str(args.status_table), "id", args.s3_profile, args.s3_endpoint)

    for case in cases:

        # Generate a uuid
        output_id = uuid.uuid4()

        slurm = open(os.path.join(args.outdir, "%s.%s.sh" %(cases[case][1], cases[case][0])), "w")
        template = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        "etc/template_hc.sh")
        temp = open(template, "r")
        for line in temp:
            if "XX_THREAD_COUNT_XX" in line:
                line = line.replace("XX_THREAD_COUNT_XX", str(args.thread_count))
            if "XX_JAVAHEAP_XX" in line:
                line = line.replace("XX_JAVAHEAP_XX", args.java_heap)                
            if "XX_MEM_XX" in line:
                line = line.replace("XX_MEM_XX", str(args.mem))
            if "XX_OUTPUT_ID_XX" in line:
                line = line.replace("XX_OUTPUT_ID_XX", str(output_id))                
            if "XX_INPUTID_XX" in line:
                line = line.replace("XX_INPUTID_XX", str(cases[case][0]))
            if "XX_PROJECT_XX" in line:
                line = line.replace("XX_PROJECT_XX", str(cases[case][1]))
            if "XX_MD5_XX" in line:
                line = line.replace("XX_MD5_XX", str(cases[case][2]))
            if "XX_S3URL_XX" in line:
                line = line.replace("XX_S3URL_XX", str(cases[case][3]))
            if "XX_S3PROFILE_XX" in line:
                line = line.replace("XX_S3PROFILE_XX", args.s3_profile)
            if "XX_S3ENDPOINT_XX" in line:
                line = line.replace("XX_S3ENDPOINT_XX", args.s3_endpoint)
            if "XX_REFDIR_XX" in line:
                line = line.replace("XX_REFDIR_XX", args.refdir)
            if "XX_S3DIR_XX" in line:
                line = line.replace("XX_S3DIR_XX", args.s3dir)
            if "XX_INPUT_TABLE_XX" in line:
                line = line.replace("XX_INPUT_TABLE_XX", args.status_table)


            slurm.write(line)
        slurm.close()
        temp.close()
