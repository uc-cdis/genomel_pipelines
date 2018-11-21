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

def get_reads(engine, genomel_fastq_input, input_primary_column="id"):
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
    return retrive_reads(cases)

def get_bams(engine, genomel_bam_input, input_primary_column="id"):
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
    return retrive_bams(cases)

def get_case_from_metrics(engine, metrics_table, genomel_fastq_input, genomel_bam_input):
    '''collect input information from metrics tables'''
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)

    # read input tables
    fastqfiles = Table(genomel_fastq_input, meta, autoload=True)
    mapper(FastqFiles, fastqfiles)
    fastq_cases = session.query(FastqFiles).all()

    bamfiles = Table(genomel_bam_input, meta, autoload=True)
    mapper(BamFiles, bamfiles)
    bam_cases = session.query(BamFiles).all()

    # read the metrics table
    metrics = Table(metrics_table, meta, autoload=True)
    mapper(Metrics, metrics)
    cases = session.query(Metrics).all()
    aliquot_ids = list()
    for row in cases:
        if row.status != 'COMPLETED':
            if row.aliquot_id not in aliquot_ids:
                aliquot_ids.append(row.aliquot_id)
    fastq_cases_filter = list([x for x in aliquot_ids \
                         if x.aliquot_id in fastq_cases])
    bam_cases_filter = list([x for x in aliquot_ids \
                       if x.aliquot_id in bam_cases])
    reads_ids = dict()
    bams_ids = dict()
    if fastq_cases_filter:
        reads_ids = retrive_reads(fastq_cases_filter)
    if bam_cases_filter:
        bams_ids = retrive_bams(bam_cases_filter)
    return {'reads_ids': reads_ids, 'bams_ids': bams_ids}
