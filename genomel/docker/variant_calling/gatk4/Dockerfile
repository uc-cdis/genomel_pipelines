FROM ubuntu:16.04

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y time \
       python-dev \
       python-pip \
       openjdk-8-jre-headless \
       wget unzip \
    && apt-get clean \
    && wget https://github.com/broadinstitute/gatk/releases/download/4.1.0.0/gatk-4.1.0.0.zip \
    && mv gatk-4.1.0.0.zip /opt/ \
    && cd /opt/ && unzip gatk-4.1.0.0.zip \
    && pip install pysam pyvcf \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /opt/gatk-4.1.0.0.zip

ADD genomel_pdc_gatk4_cohort_genotyping.py /opt/
