FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y time \
    python-dev openjdk-8-jre-headless

###GATK 3.7-0-gcfedb67
ADD GenomeAnalysisTK.jar /opt/
ADD gatk3_genomel_variant_calling.py /opt/
