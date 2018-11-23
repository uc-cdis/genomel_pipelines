'''SLURM SBATCH script'''
import os
import utils.pipeline
import postgres.utils
import postgres.status

def create_scripts(args):
    '''Builds the slurm scripts to run GenoMEL Individual pipeline'''
    # Check paths
    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: {}".format(args.outdir))
    if not os.path.isfile(args.config_local):
        raise Exception("Cannot find config file: {}".format(args.config_local))
    # Database setup
    engine = postgres.utils.get_db_engine(args.config_local)
    if args.pipeline == 'alignment':
        psql_data = postgres.status.get_reads(engine, args.input_table, args.status_table)
    elif args.pipeline == 'harmonization':
        psql_data = postgres.status.get_bams(engine, args.input_table, args.status_table)
    else:
        raise Exception("Cannot find pipeline: {}. Make sure it is `alignment`|`harmonization`".\
                        format(args.pipeline))
    script_creator = ScriptCreator(psql_data, args)
    script_creator.write_slurm_script()

class ScriptCreator(object):
    '''this class describes methods prepare SLURM script files'''
    def __init__(self, psql_data, args):
        self.psql_data = psql_data
        self.input_table = args.input_table
        self.pipeline = args.pipeline
        self.outdir = args.outdir
        self.alignment_cmd = """
        --fastq_read1_uri ${fastq_read1_uri[*]}
        --fastq_read2_uri ${fastq_read2_uri[*]}
        --fastq_read1_md5 ${fastq_read1_md5[*]}
        --fastq_read2_md5 ${fastq_read2_md5[*]}
        --readgroup_names ${readgroup_names[*]}
        """
        self.alignment_variable = """
        fastq_read1_uri=({FASTQ_READ1_URI})
        fastq_read2_uri=({FASTQ_READ2_URI})
        fastq_read1_md5=({FASTQ_READ1_MD5})
        fastq_read2_md5=({FASTQ_READ2_MD5})
        readgroup_names=({READGROUP_NAMES})
        """
        self.harmonization_cmd = """
        --bam_uri $bam_uri
        --bam_md5 $bam_md5
        """
        self.harmonization_variable = """
        bam_uri="{BAM_URI}"
        bam_md5="{BAM_MD5}"
        """

    def _separate_readgroup_meta(self, aliquot_id):
        '''exclude nonreadgroup metadata'''
        exclude_keys = ('project', 's3_profile', 's3_endpoint')
        project_meta = {key: value for key, value in self.psql_data[aliquot_id].items() \
            if key in exclude_keys}
        for k in exclude_keys:
            self.psql_data[aliquot_id].pop(k, None)
        readgroup_meta = self.psql_data[aliquot_id]
        return project_meta, readgroup_meta

    def _alignment_variables(self, aliquot_id):
        '''prepare alignment variables'''
        readgroup_meta = self._separate_readgroup_meta(aliquot_id)[1]
        read1 = []
        read2 = []
        read1_md5 = []
        read2_md5 = []
        rg_ids = []
        for rg_id, rg_meta in readgroup_meta.items():
            rg_ids += [rg_id]
            read1 += rg_meta['s3_url_r1']
            read2 += rg_meta['s3_url_r2']
            read1_md5 += rg_meta['md5_r1']
            read2_md5 += rg_meta['md5_r2']
        if len(rg_ids) != len(read1) and len(rg_ids) == 1:
            rg_ids = rg_ids * len(read1)
        shell_variables = self.alignment_variable.format(
            FASTQ_READ1_URI=' '.join('"{}"'.format(x) for x in read1),
            FASTQ_READ2_URI=' '.join('"{}"'.format(x) for x in read2),
            FASTQ_READ1_MD5=' '.join('"{}"'.format(x) for x in read1_md5),
            FASTQ_READ2_MD5=' '.join('"{}"'.format(x) for x in read2_md5),
            READGROUP_NAMES=' '.join('"{}"'.format(x) for x in rg_ids)
        )
        return shell_variables

    def _harmonization_variable(self, aliquot_id):
        '''prepare harmonization variables'''
        readgroup_meta = self._separate_readgroup_meta(aliquot_id)[1]
        shell_variables = self.harmonization_variable.format(
            BAM_URI=readgroup_meta['s3_url'],
            BAM_MD5=readgroup_meta['md5'][0]
        )
        return shell_variables

    def _prepare_pipeline_variables(self, aliquot_id):
        '''prepare pipeline variables'''
        if self.pipeline == 'alignment':
            pipeline_variables = self._alignment_variables(aliquot_id)
        elif self.pipeline == 'harmonization':
            pipeline_variables = self._harmonization_variable(aliquot_id)
        return pipeline_variables

    def _prepare_pipeline_cmd(self):
        '''prepare pipeline cmd'''
        if self.pipeline == 'alignment':
            pipeline_cmd = self.alignment_cmd
        elif self.pipeline == 'harmonization':
            pipeline_cmd = self.harmonization_cmd
        return pipeline_cmd

    def write_slurm_script(self):
        '''Writes the actual slurm script file'''
        for aliquot_id, metadata in self.psql_data.items():
            slurm = os.path.join(self.outdir, 'genomel_individual.{0}.{1}.{2}.sh'.format(
                self.pipeline, metadata['project'], aliquot_id))
            # load template
            template_str = utils.pipeline.load_template_slurm()
            # write
            val = template_str.format(
                PIPELINE=self.pipeline,
                ALIQUOT_ID=aliquot_id,
                INPUT_TABLE=self.input_table,
                PROJECT=metadata['project'],
                D_S3_PROFILE=metadata['s3_profile'],
                D_S3_ENDPOINT=metadata['s3_endpoint'],
                PIPELINE_VARIABLES=self._prepare_pipeline_variables(aliquot_id),
                PIPELINE_CMD=self._prepare_pipeline_cmd()
            )
            with open(slurm, 'w') as ohandle:
                ohandle.write(val)
