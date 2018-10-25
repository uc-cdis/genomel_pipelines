FROM ubuntu:bionic-20180426

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y time \
       python-dev \
       openjdk-11-jre-headless \
       wget git g++ gcc make zlib1g-dev libbz2-dev liblzma-dev \
    && apt-get clean \
    && wget https://github.com/broadinstitute/picard/releases/download/2.18.11/picard.jar \
    && mv picard.jar /opt/ \
    && cd /opt/ && git clone --recursive git://github.com/ekg/freebayes.git \
    && cd /opt/freebayes && make \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

###GATK 3.7-0-gcfedb67
ADD GenomeAnalysisTK.jar /opt/
ADD gatk3_genomel_variant_calling.py /opt/
