FROM ubuntu:16.04

### add novocraftV3.09.00.Linux3.1X and license
ADD novocraft.tar.bz2 /opt/

RUN apt-get update -y && \
    apt-get install -y git wget unzip time gawk\
    bzip2 gcc libncurses-dev make zlib1g-dev libbz2-dev liblzma-dev \
    openjdk-8-jre-headless

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
    && rm Trimmomatic-0.38.zip
