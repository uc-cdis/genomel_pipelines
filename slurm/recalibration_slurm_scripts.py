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

    parser = argparse.ArgumentParser(description="Genomel Recalibration CWL workflow SLURM script creator")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--thread_count", help="Thread count", required=True)
    required.add_argument("--mem", help="Max mem for each node", required=True)
    required.add_argument("--refdir", help="Reference dir on node", required=True)
    required.add_argument("--s3dir", help="S3bin for uploading output files", required=True)
    required.add_argument("--postgres_config", help="Path to postgres config file", required=True)
    required.add_argument("--outdir", default="./", help="Output directory for slurm scripts")
    required.add_argument("--cases_from_status", action='store_true', default=False, help="Get cases from input table or status")    
    required.add_argument("--input_table", help="Postgres input table name", required=True)
    required.add_argument("--status_table", default="None", help="Postgres status table name")
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: %s" %args.outdir)

    if not os.path.isfile(args.postgres_config):
        raise Exception("Cannot find config file: %s" %args.postgres_config)

    engine = postgres.utils.get_db_engine(args.postgres_config)
    if args.cases_from_status:
        cases = postgres.status.get_case_from_status(engine, str(args.input_table), str(args.status_table), input_primary_column="id")
    else:   
        cases = postgres.status.get_case(engine, str(args.input_table), str(args.status_table), input_primary_column="id")


    for case in cases:
        slurm = open(os.path.join(args.outdir, "%s.%s.sh" %(cases[case][1], cases[case][0])), "w")
        template = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        "etc/template_recalibration.sh")
        temp = open(template, "r")
        for line in temp:
            if "XX_THREAD_COUNT_XX" in line:
                line = line.replace("XX_THREAD_COUNT_XX", str(args.thread_count))
            if "XX_MEM_XX" in line:
                line = line.replace("XX_MEM_XX", str(args.mem))
            if "XX_INPUTID_XX" in line:
                line = line.replace("XX_INPUTID_XX", str(cases[case][0]))
            if "XX_PROJECT_XX" in line:
                line = line.replace("XX_PROJECT_XX", str(cases[case][1]))
            if "XX_MD5_XX" in line:
                line = line.replace("XX_MD5_XX", str(cases[case][2]))
            if "XX_S3URL_XX" in line:
                line = line.replace("XX_S3URL_XX", str(cases[case][3]))
            if "XX_S3PROFILE_XX" in line:
                line = line.replace("XX_S3PROFILE_XX", str(cases[case][4]))
            if "XX_S3ENDPOINT_XX" in line:
                line = line.replace("XX_S3ENDPOINT_XX", str(cases[case][5]))
            if "XX_REFDIR_XX" in line:
                line = line.replace("XX_REFDIR_XX", args.refdir)
            if "XX_S3DIR_XX" in line:
                line = line.replace("XX_S3DIR_XX", args.s3dir)

            slurm.write(line)
        slurm.close()
        temp.close()