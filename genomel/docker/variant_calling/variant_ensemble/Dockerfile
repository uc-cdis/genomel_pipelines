FROM ubuntu:16.04

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y time \
       openjdk-8-jre-headless \
       wget \
    && apt-get clean \
    && wget https://github.com/chapmanb/bcbio.variation/releases/download/v0.2.6/bcbio.variation-0.2.6-standalone.jar \
    && mv bcbio.variation-0.2.6-standalone.jar /opt/bcbio.variation-0.2.6-standalone.jar \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
