FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y git wget unzip gzip time \
    g++ bzip2 gcc libncurses-dev make zlib1g-dev libbz2-dev liblzma-dev \
    openjdk-8-jre-headless \
    && apt-get clean

RUN cd /opt/ && wget https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2 \
    && tar xf samtools-1.9.tar.bz2 \
    && cd samtools-1.9 \
    && make \
    && make install \
    && cd - \
    && rm -rf samtools-1.9.tar.bz2 \
    && cd /opt/ && wget https://github.com/gt1/biobambam2/releases/download/2.0.87-release-20180301132713/biobambam2-2.0.87-release-20180301132713-x86_64-etch-linux-gnu.tar.gz \
    && tar xf biobambam2-2.0.87-release-20180301132713-x86_64-etch-linux-gnu.tar.gz \
    && rm biobambam2-2.0.87-release-20180301132713-x86_64-etch-linux-gnu.tar.gz \
    && cd /opt/ && wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.38.zip \
    && unzip Trimmomatic-0.38.zip \
    && rm Trimmomatic-0.38.zip \
    && cd /opt/ && wget https://github.com/biod/sambamba/releases/download/v0.6.8/sambamba-0.6.8-linux-static.gz \
    && gzip -d sambamba-0.6.8-linux-static.gz && chmod +x sambamba-0.6.8-linux-static \
    && cd /opt/ && wget https://github.com/GregoryFaust/samblaster/releases/download/v.0.1.24/samblaster-v.0.1.24.tar.gz \
    && tar xf samblaster-v.0.1.24.tar.gz \
    && cd samblaster-v.0.1.24 \
    && make && rm /opt/samblaster-v.0.1.24.tar.gz \
    && cd /opt/ && wget https://github.com/lh3/bwa/releases/download/v0.7.17/bwa-0.7.17.tar.bz2 \
    && tar xf bwa-0.7.17.tar.bz2 \
    && cd bwa-0.7.17 \
    && make && rm /opt/bwa-0.7.17.tar.bz2 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
