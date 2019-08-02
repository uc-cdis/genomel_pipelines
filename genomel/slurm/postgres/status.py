'''
Postgres tables for the PDC CWL Workflow
'''
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy import Column, String

class Metrics(object):
    pass

class BamFiles(object):
    pass

class FastqFiles(object):
    pass

def retrive_reads(cases):
    '''Organize rows of genomel_fastq_input to dictionary'''
    s = dict()
    for row in cases:
        s.setdefault(row.aliquot_id, {})
        s[row.aliquot_id].setdefault(row.read_group, {})
        s[row.aliquot_id][row.read_group].setdefault('input_id_r1', [])
        s[row.aliquot_id][row.read_group]['input_id_r1'].append(row.input_id_r1)
        s[row.aliquot_id][row.read_group].setdefault('input_id_r2', [])
        s[row.aliquot_id][row.read_group]['input_id_r2'].append(row.input_id_r2)
        s[row.aliquot_id][row.read_group].setdefault('md5_r1', [])
        s[row.aliquot_id][row.read_group]['md5_r1'].append(row.md5_r1)
        s[row.aliquot_id][row.read_group].setdefault('md5_r2', [])
        s[row.aliquot_id][row.read_group]['md5_r2'].append(row.md5_r2)
        s[row.aliquot_id][row.read_group].setdefault('s3_url_r1', [])
        s[row.aliquot_id][row.read_group]['s3_url_r1'].append(row.s3_url_r1)
        s[row.aliquot_id][row.read_group].setdefault('s3_url_r2', [])
        s[row.aliquot_id][row.read_group]['s3_url_r2'].append(row.s3_url_r2)
        s[row.aliquot_id]['s3_profile'] = row.s3_profile
        s[row.aliquot_id]['s3_endpoint'] = row.s3_endpoint
        s[row.aliquot_id]['project'] = row.project
    return s

def retrive_bams(cases):
    '''Organize rows of genomel_bam_input to dictionary'''
    s = dict()
    for row in cases:
        s.setdefault(row.aliquot_id, {})
        s[row.aliquot_id].setdefault('input_id', [])
        s[row.aliquot_id]['input_id'].append(row.input_id)
        s[row.aliquot_id].setdefault('md5', [])
        s[row.aliquot_id]['md5'].append(row.md5)
        s[row.aliquot_id].setdefault('s3_url', [])
        s[row.aliquot_id]['s3_url'].append(row.s3_url)
        s[row.aliquot_id]['s3_profile'] = row.s3_profile
        s[row.aliquot_id]['s3_endpoint'] = row.s3_endpoint
        s[row.aliquot_id]['project'] = row.project
    return s

def get_reads(engine, genomel_fastq_input, status_table, input_primary_column="id"):
    '''collect input information from genomel_fastq_input tables'''
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    # read the input table
    data = Table(genomel_fastq_input, meta,
                 Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(FastqFiles, data)
    cases = session.query(FastqFiles).all()
    if status_table:
        s = dict()
        # read the status table
        metrics = Table(status_table, meta, autoload=True)
        mapper(Metrics, metrics)
        for row in cases:
            processed = session.query(Metrics).filter(Metrics.aliquot_id == row.aliquot_id).all()
            rexecute = True
            for processed_case in processed:
                if processed_case and processed_case.status == 'COMPLETED':
                    rexecute = False
            if rexecute:
                s.setdefault(row.aliquot_id, {})
                s[row.aliquot_id].setdefault(row.read_group, {})
                s[row.aliquot_id][row.read_group].setdefault('input_id_r1', [])
                s[row.aliquot_id][row.read_group]['input_id_r1'].append(row.input_id_r1)
                s[row.aliquot_id][row.read_group].setdefault('input_id_r2', [])
                s[row.aliquot_id][row.read_group]['input_id_r2'].append(row.input_id_r2)
                s[row.aliquot_id][row.read_group].setdefault('md5_r1', [])
                s[row.aliquot_id][row.read_group]['md5_r1'].append(row.md5_r1)
                s[row.aliquot_id][row.read_group].setdefault('md5_r2', [])
                s[row.aliquot_id][row.read_group]['md5_r2'].append(row.md5_r2)
                s[row.aliquot_id][row.read_group].setdefault('s3_url_r1', [])
                s[row.aliquot_id][row.read_group]['s3_url_r1'].append(row.s3_url_r1)
                s[row.aliquot_id][row.read_group].setdefault('s3_url_r2', [])
                s[row.aliquot_id][row.read_group]['s3_url_r2'].append(row.s3_url_r2)
                s[row.aliquot_id]['s3_profile'] = row.s3_profile
                s[row.aliquot_id]['s3_endpoint'] = row.s3_endpoint
                s[row.aliquot_id]['project'] = row.project
        return s
    return retrive_reads(cases)

def get_bams(engine, genomel_bam_input, status_table, input_primary_column="id"):
    '''collect input information from genomel_bam_input tables'''
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    # read the input table
    data = Table(genomel_bam_input, meta,
                 Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(BamFiles, data)
    cases = session.query(BamFiles).all()
    if status_table:
        s = dict()
        # read the status table
        metrics = Table(status_table, meta, autoload=True)
        mapper(Metrics, metrics)
        for row in cases:
            processed = session.query(Metrics).filter(Metrics.aliquot_id == row.aliquot_id).all()
            rexecute = True
            for processed_case in processed:
                if processed_case and processed_case.status == 'COMPLETED':
                    rexecute = False
            if rexecute:
                s.setdefault(row.aliquot_id, {})
                s[row.aliquot_id].setdefault('input_id', [])
                s[row.aliquot_id]['input_id'].append(row.input_id)
                s[row.aliquot_id].setdefault('md5', [])
                s[row.aliquot_id]['md5'].append(row.md5)
                s[row.aliquot_id].setdefault('s3_url', [])
                s[row.aliquot_id]['s3_url'].append(row.s3_url)
                s[row.aliquot_id]['s3_profile'] = row.s3_profile
                s[row.aliquot_id]['s3_endpoint'] = row.s3_endpoint
                s[row.aliquot_id]['project'] = row.project
        return s
    return retrive_bams(cases)

def get_metrics(engine, input_table):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    data = Table(input_table, meta, autoload=True)
    mapper(Metrics, data)
    cases = session.query(Metrics).all()
    prod_time = list()
    total = list()
    passed = list()
    failed = list()
    for row in cases:
        prod_time.append(row.prod_time)
        total.append(row.nchunk_total)
        passed.append(row.nchunk_passed)
        failed.append(row.nchunk_failed)
        indiv_pass_time = row.indiv_pass_time
        indiv_fail_time = row.indiv_fail_time
        indiv_pass_mem = row.indiv_pass_mem
        indiv_fail_mem = row.indiv_fail_mem
    return prod_time, total, passed, failed, indiv_pass_time, indiv_fail_time, indiv_pass_mem, indiv_fail_mem
