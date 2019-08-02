FROM ubuntu:16.04

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y time \
       python-dev \
       tabix \
       pkg-config \
       openjdk-8-jre-headless \
       wget git g++ gcc make zlib1g-dev libbz2-dev liblzma-dev \
    && apt-get clean \
    && wget https://github.com/broadinstitute/picard/releases/download/2.18.11/picard.jar \
    && mv picard.jar /opt/ \
    && wget https://github.com/vcftools/vcftools/releases/download/v0.1.16/vcftools-0.1.16.tar.gz \
    && mv vcftools-0.1.16.tar.gz /opt/ \
    && cd /opt/ && tar xvf vcftools-0.1.16.tar.gz \
    && cd vcftools-0.1.16 \
    && ./configure \
    && make \
    && make install \
    && cd - \
    && rm -rf vcftools-0.1.16.tar.gz vcftools-0.1.16\
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

###GATK 3.7-0-gcfedb67
ADD GenomeAnalysisTK.jar /opt/ &&
ADD snpEff.jar /opt/
ADD SnpSift.jar /opt/
ADD modify_header.sh /opt/

