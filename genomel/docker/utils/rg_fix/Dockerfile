FROM ubuntu:xenial-20210416

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y time \
       python-dev \
       openjdk-8-jre-headless \
       wget \
    && apt-get clean \
    && wget https://github.com/broadinstitute/picard/releases/download/2.18.11/picard.jar \
    && mv picard.jar /opt/ \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD rg_fix.py /opt/
