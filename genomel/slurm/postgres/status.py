'''
Postgres tables for the PDC CWL Workflow
'''
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy import Column, String


class State(object):
    pass


class Files(object):
    pass


def get_reads(engine, genomel_fastq_input, input_primary_column="id"):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    # read the input table
    data = Table(genomel_fastq_input, meta, Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(Files, data)
    s = dict()
    cases = session.query(Files).all()
    for row in cases:
        s.setdefault(row.aliquot, {})
        s[row.aliquot].setdefault(row.read_group, {})
        s[row.aliquot][row.read_group].setdefault('input_id_r1', [])
        s[row.aliquot][row.read_group]['input_id_r1'].append(row.input_id_r1)
        s[row.aliquot][row.read_group].setdefault('input_id_r2', [])
        s[row.aliquot][row.read_group]['input_id_r2'].append(row.input_id_r2)
        s[row.aliquot][row.read_group].setdefault('md5_r1', [])
        s[row.aliquot][row.read_group]['md5_r1'].append(row.md5_r1)
        s[row.aliquot][row.read_group].setdefault('md5_r2', [])
        s[row.aliquot][row.read_group]['md5_r2'].append(row.md5_r2)
        s[row.aliquot][row.read_group].setdefault('size_r1', [])
        s[row.aliquot][row.read_group]['size_r1'].append(row.size_r1)
        s[row.aliquot][row.read_group].setdefault('size_r2', [])
        s[row.aliquot][row.read_group]['size_r2'].append(row.size_r2)
        s[row.aliquot][row.read_group].setdefault('s3_url_r1', [])
        s[row.aliquot][row.read_group]['s3_url_r11'].append(row.s3_url_r1)
        s[row.aliquot][row.read_group].setdefault('s3_url_r2', [])
        s[row.aliquot][row.read_group]['s3_url_r2'].append(row.s3_url_r2)
        s[row.aliquot]['s3_profile'] = row.s3_profile
        s[row.aliquot]['s3_endpoint'] = row.s3_endpoint
        s[row.aliquot]['project'] = row.project
    return s


def get_case(engine, genomel_bam_input, input_primary_column="id"):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    # read the input table
    data = Table(genomel_bam_input, meta, Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(Files, data)
    s = dict()
    cases = session.query(Files).all()
    for row in cases:
        s.setdefault(row.aliquot, {})
        s[row.aliquot].setdefault('input_id', [])
        s[row.aliquot]['input_id'].append(row.input_id)
        s[row.aliquot].setdefault('md5', [])
        s[row.aliquot]['md5'].append(row.md5)
        s[row.aliquot].setdefault('s3_url', [])
        s[row.aliquot]['s3_url'].append(row.s3_url)
        s[row.aliquot].setdefault('file_size', [])
        s[row.aliquot]['file_size'].append(row.file_size)
        s[row.aliquot]['s3_profile'] = row.s3_profile
        s[row.aliquot]['s3_endpoint'] = row.s3_endpoint
        s[row.aliquot]['project'] = row.project
    return s


# def get_case_from_metrics(engine, metrics_table, input_primary_column, profile, endpoint, input_table=None):
#     Session = sessionmaker()
#     Session.configure(bind=engine)
#     session = Session()
#     meta = MetaData(engine)

#     # read the status table
#     state = Table(metrics_table, meta, autoload=True)
#     mapper(State, state)

#     # collect input information from metrics tables
#     s = dict()
#     cases = session.query(State).all()
#     for row in cases:
#         if row.status == 'COMPLETED':
#             if not input_table or (input_table and row.input_table == input_table):
#                 s[count] = [row.output_id,
#                             row.project,
#                             row.md5,
#                             row.s3_url,
#                             profile,
#                             endpoint]
#                 count += 1

#     return s
