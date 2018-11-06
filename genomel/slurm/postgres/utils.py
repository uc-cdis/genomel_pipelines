from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy.engine.reflection import Inspector
from contextlib import contextmanager

Base = declarative_base()


def get_db_engine(pg_config):
  ''' Establishes connection '''
  s = open(pg_config, 'r').read()
  postgres_config = eval(s)

  DATABASE = {
      'drivername': 'postgres',
      'host': '172.16.132.255',
      'port': '5432',
      'username': postgres_config['username'],
      'password': postgres_config['password'],
      'database': 'prod_bioinfo'
  }

  return __db_connect(DATABASE)


@contextmanager
def session_scope():
  """ Provide a transactional scope around a series of transactions """

  session = Session()
  try:
    yield session
    session.commit()
  except:
    session.rollback()
    raise
  finally:
    session.close()


def __db_connect(database):
  """performs database connection"""

  return create_engine(URL(**database))


def create_table(engine, tool):
  """ checks if a table for metrics exists and create one if it doesn't """

  inspector = Inspector.from_engine(engine)
  tables = set(inspector.get_table_names())
  if tool.__tablename__ not in tables:
    Base.metadata.create_all(engine)


def add_metrics(engine, met):
  """ add provided metrics to database """
  Session = sessionmaker()
  Session.configure(bind=engine)
  session = Session()

  session.add(met)
  session.commit()
  session.expunge_all()
  session.close()


class State(object):
  pass


class Metrics(object):
  pass


def update_record_metrics(engine, table, met):
  """ update provided metrics to database if record exist"""

  Session = sessionmaker()
  Session.configure(bind=engine)
  session = Session()
  meta = MetaData(engine)
  state = Table(table.__tablename__, meta, autoload=True)
  mapper(State, state)
  record = session.query(State).filter(State.uuid == met.uuid).first()

  if record:
    record.input_id = met.input_id
    record.input_table = met.input_table
    record.project = met.project
    record.status = met.status
    record.datetime_start = met.datetime_start
    record.datetime_end = met.datetime_end
    record.download_time = met.download_time
    record.bam_upload_time = met.bam_upload_time
    record.gvcf_upload_time = met.gvcf_upload_time
    record.bam_url = met.bam_url
    record.gvcf_url = met.gvcf_url
    record.bam_md5sum = met.bam_md5sum
    record.gvcf_md5sum = met.gvcf_md5sum
    record.bam_filesize = met.bam_filesize
    record.gvcf_filesize = met.gvcf_filesize
    record.harmonization_cwl_walltime = met.harmonization_cwl_walltime
    record.harmonization_cwl_cpu_percentage = met.harmonization_cwl_cpu_percentage
    record.realignment_cwl_walltime = met.realignment_cwl_walltime
    record.realignment_cwl_cpu_percentage = met.realignment_cwl_cpu_percentage
    record.haplotypecaller_cwl_walltime = met.haplotypecaller_cwl_walltime
    record.haplotypecaller_cwl_cpu_percentage = met.haplotypecaller_cwl_cpu_percentage
    record.whole_workflow_elapsed = met.whole_workflow_elapsed,
    record.hostname = met.hostname,
    record.cwl_version = met.cwl_version,
    record.docker_version = met.docker_version,
    record.cwl_input_json = met.cwl_input_json,
    record.time_metrics_json = met.time_metrics_json

    session.flush()
    session.commit()
    session.expunge_all()
    session.close()

  return record


def add_pipeline_metrics(engine, project, uuid, input_id, input_table, status, datetime_start, datetime_end, download_time, bam_upload_time, gvcf_upload_time, bam_url, gvcf_url, bam_md5sum, gvcf_md5sum, bam_filesize, gvcf_filesize, harmonization_cwl_walltime, harmonization_cwl_cpu_percentage, realignment_cwl_walltime, realignment_cwl_cpu_percentage, haplotypecaller_cwl_walltime, haplotypecaller_cwl_cpu_percentage, whole_workflow_elapsed, hostname, cwl_version, docker_version, cwl_input_json, time_metrics_json, metricsclass):
  """ add provided status to database """
  met = metricsclass(job_uuid=uuid,
                     input_id=input_id,
                     input_table=input_table,
                     project=project,
                     status=status,
                     datetime_start=datetime_start,
                     datetime_end=datetime_end,
                     download_time=download_time,
                     bam_upload_time=bam_upload_time,
                     gvcf_upload_time=gvcf_upload_time,
                     bam_url=bam_url,
                     gvcf_url=gvcf_url,
                     bam_md5sum=bam_md5sum,
                     gvcf_md5sum=gvcf_md5sum,
                     bam_filesize=bam_filesize,
                     gvcf_filesize=gvcf_filesize,
                     harmonization_cwl_walltime=harmonization_cwl_walltime,
                     harmonization_cwl_cpu_percentage=harmonization_cwl_cpu_percentage,
                     realignment_cwl_walltime=realignment_cwl_walltime,
                     realignment_cwl_cpu_percentage=realignment_cwl_cpu_percentage,
                     haplotypecaller_cwl_walltime=haplotypecaller_cwl_walltime,
                     haplotypecaller_cwl_cpu_percentage=haplotypecaller_cwl_cpu_percentage,
                     whole_workflow_elapsed=whole_workflow_elapsed,
                     hostname=hostname,
                     cwl_version=cwl_version,
                     docker_version=docker_version,
                     cwl_input_json=cwl_input_json,
                     time_metrics_json=time_metrics_json)

  # create table if not present
  create_table(engine, met)

  record = update_record_metrics(engine, metricsclass, met)
  if not record:
    add_metrics(engine, met)


def set_download_error(exit_code, logger, engine, project, uuid, input_id, input_table, datetime_start, datetime_end, hostname, cwl_version, docker_version, download_time, whole_workflow_elapsed, metricsclass):
  ''' Sets the status for download errors '''
  if exit_code != 0:
    logger.info("Input file download error")
    status = "DOWNLOAD_FAILURE"
  else:
    logger.info("Md5 unmatch error")
    status = "UNMATCHED_MD5"
  add_pipeline_metrics(engine, project, uuid, input_id, input_table, status, datetime_start, datetime_end, download_time, float(0), float(0), str(0), str(0), str(0), str(0), float(0), float(0), float(0), float(0), float(0), float(0), float(0), float(0), whole_workflow_elapsed, hostname, cwl_version, docker_version, str(0), str(0), metricsclass)
