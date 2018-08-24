'''
Postgres mixins
'''
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager

class InputTypeMixin(object):
    """ Gather information about processing status """
    id               = Column(Integer, primary_key=True)
    input_id         = Column(String)
    project          = Column(String)
    md5              = Column(String)
    file_size        = Column(String)
    s3_url           = Column(String)
    s3_profile       = Column(String)    
    s3_endpoint      = Column(String)

    def __repr__(self):
        return "<InputTypeMixin(uuid='%s', status='%s' , s3_url='%s')>" %(self.uuid, self.status, self.s3_url)


class StatusTypeMixin(object):
    """ Gather information about processing status """
    id               = Column(Integer, primary_key=True)
    uuid             = Column(String)
    project          = Column(String)
    input_id         = Column(ARRAY(String))
    input_table      = Column(String)  
    output_id        = Column(String)
    status           = Column(String)
    s3_url           = Column(String)
    datetime_start   = Column(String)
    datetime_end     = Column(String)
    md5              = Column(String)
    file_size        = Column(String)
    hostname         = Column(String)
    cwl_version      = Column(String)
    docker_version   = Column(ARRAY(String))

    def __repr__(self):
        return "<StatusTypeMixin(uuid='%s', status='%s' , s3_url='%s')>" %(self.uuid, self.status, self.s3_url)

class MetricsTypeMixin(object):
    ''' Gather timing metrics with input uuids '''
    id                                 = Column(Integer, primary_key=True)
    uuid                               = Column(String)
    input_id                           = Column(ARRAY(String))
    input_table                        = Column(String)      
    download_time                      = Column(String)
    upload_time                        = Column(String)
    thread_count                       = Column(String)
    whole_workflow_elapsed             = Column(String)
    main_cwl_systime                   = Column(Float)
    main_cwl_usertime                  = Column(Float)
    main_cwl_walltime                  = Column(String)
    main_cwl_percent_of_cpu            = Column(Float)
    main_cwl_maximum_resident_set_size = Column(Float)
    status                             = Column(String)

    def __repr__(self):
        return "<TimeToolTypeMixin(uuid='%s', elapsed='%s', status='%s')>" %(self.uuid, self.elapsed, self.status)