FROM ubuntu:xenial-20210416

RUN apt-get update -y && \
    apt-get install -y time \
    openjdk-8-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

###GATK 3.7-0-gcfedb67
ADD GenomeAnalysisTK.jar /opt/
