FROM ubuntu:artful-20171019

RUN apt-get update \
    && apt-get install -y time \
       awscli \
       dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
