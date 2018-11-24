'''GenoMEL-Bionimbus Protected Data Cloud SLURM runner'''

import argparse
import utils.workflow

def get_args():
    '''Loads the parser'''
    # Main parser
    parser = argparse.ArgumentParser(prog='GenoMEL-Bionimbus Protected Data Cloud SLURM runner.', \
                                     add_help=False)
    # Required parser
    required = parser.add_argument_group("Required input parameters")
    required.add_argument('--job_uuid', \
                          required=True, \
                          help='Job UUID')
    required.add_argument('--basedir', \
                          required=True, \
                          help='Base work directory')
    required.add_argument('--cwlwf', \
                          required=True, \
                          help='CWL main workflow runner path')
    required.add_argument('--aliquot_id', \
                          required=True, \
                          help='Aliquot ID')
    required.add_argument('--input_table', \
                          required=True, \
                          help='PSQL input table')
    required.add_argument('--project', \
                          required=True, \
                          help='GenoMEL data project')
    required.add_argument('--download_s3_profile', \
                          required=True, \
                          help='Download s3 profile')
    required.add_argument('--download_s3_endpoint', \
                          required=True, \
                          help='Download s3 endpoint url')
    required.add_argument('--psql_conf', \
                          required=True, \
                          help='Local psql conf')
    # Sub parser
    subparsers = parser.add_subparsers(help='Choose the pipeline you want to run', dest='choice')
    # Alignment
    alignment = subparsers.add_parser('alignment', help='Run alignment', \
                                      parents=[parser])
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
    # Harmonization
    harmonization = subparsers.add_parser('harmonization', help='Run harmonization', \
                                          parents=[parser])
    harmonization.add_argument('--bam_uri', \
                               required=True, \
                               help='BAM URI.')
    harmonization.add_argument('--bam_md5', \
                               required=True, \
                               help='BAM MD5.')
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
