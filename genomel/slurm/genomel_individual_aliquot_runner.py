'''GenoMEL-Bionimbus Protected Data Cloud SLURM runner'''

import argparse
import utils.workflow

def get_args():
    '''Loads the parser'''
    # Main parser
    parser = argparse.ArgumentParser(prog='GenoMEL-Bionimbus Protected Data Cloud SLURM runner.', \
                                     add_help=False)
    # Sub parser
    subparsers = parser.add_subparsers(help='Choose the pipeline you want to run', dest='choice')
    # Alignment
    alignment = subparsers.add_parser('alignment', help='Run alignment')
    alignment.add_argument('--fastq_read1_uri', \
                           required=True, \
                           nargs='+', \
                           help='Fastq read1 URI.')
    alignment.add_argument('--fastq_read2_uri', \
                           required=True, \
                           nargs='+', \
                           help='Fastq read2 URI.')
    alignment.add_argument('--fastq_read1_md5', \
                           required=True, \
                           nargs='+', \
                           help='Fastq read1 MD5.')
    alignment.add_argument('--fastq_read2_md5', \
                           required=True, \
                           nargs='+', \
                           help='Fastq read2 MD5.')
    alignment.add_argument('--readgroup_names', \
                           required=True, \
                           nargs='+', \
                           help='Read group IDs.')
    alignment.add_argument('--job_uuid', \
                          required=True, \
                          help='Job UUID')
    alignment.add_argument('--basedir', \
                          required=True, \
                          help='Base work directory')
    alignment.add_argument('--cwlwf', \
                          required=True, \
                          help='CWL main workflow runner path')
    alignment.add_argument('--aliquot_id', \
                          required=True, \
                          help='Aliquot ID')
    alignment.add_argument('--input_table', \
                          required=True, \
                          help='PSQL input table')
    alignment.add_argument('--project', \
                          required=True, \
                          help='GenoMEL data project')
    alignment.add_argument('--download_s3_profile', \
                          required=True, \
                          help='Download s3 profile')
    alignment.add_argument('--download_s3_endpoint', \
                          required=True, \
                          help='Download s3 endpoint url')
    alignment.add_argument('--psql_conf', \
                          required=True, \
                          help='Local psql conf')
    # Harmonization
    harmonization = subparsers.add_parser('harmonization', help='Run harmonization')
    harmonization.add_argument('--bam_uri', \
                               required=True, \
                               help='BAM URI.')
    harmonization.add_argument('--bam_md5', \
                               required=True, \
                               help='BAM MD5.')
    harmonization.add_argument('--job_uuid', \
                               required=True, \
                               help='Job UUID')
    harmonization.add_argument('--basedir', \
                               required=True, \
                               help='Base work directory')
    harmonization.add_argument('--cwlwf', \
                               required=True, \
                               help='CWL main workflow runner path')
    harmonization.add_argument('--aliquot_id', \
                               required=True, \
                               help='Aliquot ID')
    harmonization.add_argument('--input_table', \
                               required=True, \
                               help='PSQL input table')
    harmonization.add_argument('--project', \
                               required=True, \
                               help='GenoMEL data project')
    harmonization.add_argument('--download_s3_profile', \
                               required=True, \
                               help='Download s3 profile')
    harmonization.add_argument('--download_s3_endpoint', \
                               required=True, \
                               help='Download s3 endpoint url')
    harmonization.add_argument('--psql_conf', \
                               required=True, \
                               help='Local psql conf')
    return parser.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Run pipeline
    if args.choice == 'alignment':
        utils.workflow.run_alignment(args)
    elif args.choice == 'harmonization':
        utils.workflow.run_harmonization(args)
    else: raise Exception("Cannot find pipeline. Make sure it is `alignment`|`harmonization`")
