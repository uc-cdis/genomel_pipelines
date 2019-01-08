FROM ubuntu:18.04

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y time \
       openjdk-8-jre-headless \
       leiningen \
       wget gcc make libbz2-dev zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev\
    && apt-get clean \
    && cd /opt/ && wget https://github.com/chapmanb/bcbio.variation.recall/archive/v0.1.9.tar.gz \
    && tar xf v0.1.9.tar.gz && rm /opt/v0.1.9.tar.gz && cd /opt/bcbio.variation.recall-0.1.9/ && make \
    && cd /opt/ && wget https://github.com/samtools/htslib/releases/download/1.9/htslib-1.9.tar.bz2 \
    && tar xf htslib-1.9.tar.bz2 && rm /opt/htslib-1.9.tar.bz2 && cd /opt/htslib-1.9/ && make && make install \
    && cd /opt/ && wget https://github.com/samtools/bcftools/releases/download/1.9/bcftools-1.9.tar.bz2 \
    && tar xf bcftools-1.9.tar.bz2 && rm /opt/bcftools-1.9.tar.bz2 && cd /opt/bcftools-1.9/ && make && make install \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
