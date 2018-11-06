import postgres.status
import postgres.utils
import postgres.mixins
import logging


def setup_logging(level, log_name, log_filename):
    '''
    Sets up a logger
    '''
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    if log_filename is None:
        sh = logging.StreamHandler()
    else:
        sh = logging.FileHandler(log_filename, mode='w')

    sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(sh)
    return logger


if __name__ == '__main__':
    engine = postgres.utils.get_db_engine("pg_config")
    logger = setup_logging(logging.INFO, "abcdefg", "log_file")

    class Metrics(postgres.mixins.IndMetricsTypeMixin, postgres.utils.Base):
        __tablename__ = 'genomel_individual_pipeline'
    postgres.utils.set_download_error(1, logger, engine, "genomel-NCI-CMMUSA", "bff691d0-6cae-411c-92a5-2ddf046f2a73", ["bcba379a-25e4-4361-8c18-f05c89cd25e6"], "genomel_bam_input_table", "2018-10-30 21:29:08.995812", "2018-10-30 23:44:42.964551", "lac-planx-slurm-worker-11", "1.0.20170224141733", "registry.gitlab.com/uc-cdis/genomel-secondary-analysis:0.1b", "46", "1102939", Metrics)
    return(postgres.status.get_reads(engine, "genomel_fastq_input", input_primary_column='id'))
