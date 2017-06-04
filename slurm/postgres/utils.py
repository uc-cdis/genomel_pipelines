from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
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

class State(object):
    pass

class Files(object):
    pass

def update_record_status(engine, table, met):
    """ update provided status to database if record exist"""

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    state = Table(table.__tablename__, meta, autoload=True)
    mapper(State, state)
    record = session.query(State).filter(State.uuid == met.uuid).first()

    if record:
        record.output_id         = met.output_id
        record.status            = met.status
        record.s3_url            = met.s3_url
        record.datetime_start    = met.datetime_start
        record.datetime_end      = met.datetime_end
        record.md5               = met.md5
        record.file_size         = met.file_size
        record.hostname          = met.hostname
        record.cwl_version       = met.cwl_version
        record.docker_version    = met.docker_version       

        session.flush()
        session.commit()
        session.expunge_all()
        session.close()

    return record

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
        record.download_time                        = met.download_time
        record.upload_time                          = met.upload_time
        record.thread_count                         = met.thread_count
        record.whole_workflow_elapsed               = met.whole_workflow_elapsed
        record.main_cwl_systime                     = met.main_cwl_systime
        record.main_cwl_usertime                    = met.main_cwl_usertime
        record.main_cwl_walltime                    = met.main_cwl_walltime
        record.main_cwl_percent_of_cpu              = met.main_cwl_percent_of_cpu
        record.main_cwl_maximum_resident_set_size   = met.main_cwl_maximum_resident_set_size
        record.status                               = met.status

        session.flush()
        session.commit()
        session.expunge_all()
        session.close()

    return record

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

    record = update_record_status(engine, statusclass, met)
    if not record:
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

    record = update_record_status(engine, statusclass, met)
    if not record:
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