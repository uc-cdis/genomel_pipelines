'''
Postgres tables for the PDC CWL Workflow
'''
import postgres.utils
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy import Column, String

def get_status(upload_exit, cwl_exit, upload_file_location, upload_dir_location, logger):
    """ update the status of job on postgres """
    loc = 'UNKNOWN'
    status = 'UNKNOWN'
    if upload_exit == 0:
        loc = upload_file_location
        if cwl_exit == 0:
            status = 'COMPLETED'
            logger.info("uploaded all files to object store. The path is: %s" % upload_dir_location)
        else:
            status = 'CWL_FAILED'
            logger.info("CWL failed. The log path is: %s" % upload_dir_location)
    else:
        loc = 'Not Applicable'
        if cwl_exit == 0:
            status = 'UPLOAD_FAILURE'
            logger.info("Upload of files failed")
        else:
            status = 'FAILED'
            logger.info("CWL and upload both failed")
    return(status, loc)

class State(object):
    pass

class Files(object):
    pass

def get_case(engine, input_table, status_table, input_primary_column="id"):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    #read the input table
    data = Table (input_table, meta, Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(Files, data)
    count = 0
    s = dict()
    cases = session.query(Files).all()
    if status_table == "None":
        for row in cases:
            s[count] = [row.input_id,
                        row.project,
                        row.md5,
                        row.s3_url,
                        row.s3_profile,
                        row.s3_endpoint]
            count += 1
    else:
        #read the status table
        state = Table(status_table, meta, autoload=True)
        mapper(State, state)
        for row in cases:
            completion = session.query(State).filter(State.input_id[0] == row.input_id).first()
            if completion == None or not(completion.status == 'COMPLETED'):
                s[count] = [row.input_id,
                            row.project,
                            row.md5,
                            row.s3_url,
                            row.s3_profile,
                            row.s3_endpoint]
                count += 1
    return s

def get_case_from_status(engine, input_table, status_table, input_primary_column="id"):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)

    #read the input table
    data = Table (input_table, meta, Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(Files, data)
    
    #read the input table
    state = Table(status_table, meta, autoload=True)  
    mapper(State, state)
    
    # collect input information from status and/or input tables
    count = 0
    s = dict()    
    cases = session.query(State).all()
    for row in cases:
        completion = session.query(Files).filter(Files.input_id == row.input_id[0]).first()
        if row.status == 'COMPLETED':
            s[count] = [row.output_id,
                        completion.project,
                        row.md5,
                        row.s3_url,
                        completion.s3_profile,
                        completion.s3_endpoint]        
            count += 1

    return s