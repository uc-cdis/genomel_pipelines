from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import exc
from contextlib import contextmanager

Base = declarative_base()

def get_db_engine(pg_config):
    ''' Establishes connection '''
    s = open(pg_config, 'r').read()
    postgres_config = eval(s)

    DATABASE = {
        'drivername': 'postgres',
        'host' : '172.16.132.255',
        'port' : '5432',
        'username': postgres_config['username'],
        'password' : postgres_config['password'],
        'database' : 'prod_bioinfo'
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

    #create table if not present
    create_table(engine, met)

    session.add(met)
    session.commit()
    session.expunge_all()
    session.close()

def add_pipeline_status(engine, uuid, input_id, output_id,
                        status, s3_url, datetime_start, datetime_end,
                        md5, file_size, hostname, cwl_version, docker_version, statusclass):
    """ add provided status to database """
    met = statusclass(uuid              = uuid,
                      input_id          = input_id,
                      output_id         = output_id,
                      status            = status,
                      s3_url            = s3_url,
                      datetime_start    = datetime_start,
                      datetime_end      = datetime_end,
                      md5               = md5,
                      file_size         = file_size,
                      hostname          = hostname,
                      cwl_version       = cwl_version,
                      docker_version    = docker_version)
    create_table(engine, met)
    add_metrics(engine, met)

def add_pipeline_metrics(engine, uuid, input_id, download_time,
                         upload_time, thread_count, whole_workflow_elapsed, main_cwl_systime,
                         main_cwl_usertime, main_cwl_walltime, main_cwl_percent_of_cpu,
                         main_cwl_maximum_resident_set_size, status, metricsclass):
    """ add provided metrics to database """
    met = metricsclass(uuid                                 = uuid,
                       input_id                             = input_id,
                       download_time                        = download_time,
                       upload_time                          = upload_time,
                       thread_count                         = thread_count,
                       whole_workflow_elapsed               = whole_workflow_elapsed,
                       main_cwl_systime                     = main_cwl_systime,
                       main_cwl_usertime                    = main_cwl_usertime,
                       main_cwl_walltime                    = main_cwl_walltime,
                       main_cwl_percent_of_cpu              = main_cwl_percent_of_cpu,
                       main_cwl_maximum_resident_set_size   = main_cwl_maximum_resident_set_size,
                       status                               = status)
    create_table(engine, met)
    add_metrics(engine, met)

def set_download_error(exit_code, logger, engine,
                       uuid, input_id, output_id,
                       datetime_start, datetime_end,
                       hostname, cwl_version, docker_version,
                       download_time, whole_workflow_elapsed, statusclass, metricsclass):
    ''' Sets the status for download errors '''
    s3_url="NULL"
    md5="NULL"
    file_size="NULL"
    thread_count="s3_mcr_8"
    if exit_code != 0:
        logger.info("Input file download error")
        status = "DOWNLOAD_FAILURE"
        add_pipeline_status(engine, uuid, input_id, output_id,
                            status, s3_url, datetime_start, datetime_end,
                            md5, file_size, hostname, cwl_version, docker_version, statusclass)
        add_pipeline_metrics(engine, uuid, input_id, download_time, float(0),
                             thread_count, whole_workflow_elapsed, float(0), float(0), float(0),
                             float(0), float(0), status, metricsclass)
    else:
        logger.info("Md5 unmatch error")
        status = "UNMATCHED_MD5"
        add_pipeline_status(engine, uuid, input_id, output_id,
                            status, s3_url, datetime_start, datetime_end,
                            md5, file_size, hostname, cwl_version, docker_version, statusclass)
        add_pipeline_metrics(engine, uuid, input_id, download_time, float(0),
                             thread_count, whole_workflow_elapsed, float(0), float(0), float(0),
                             float(0), float(0), status, metricsclass)