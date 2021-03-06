FROM kbase/kbase:sdkbase.latest
# FROM kbase/kbase:interprodata
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

# RUN apt-get update

# -----------------------------------------

RUN apt-get install libffi-dev libssl-dev
RUN pip install --upgrade requests[security]
RUN apt-add-repository ppa:webupd8team/java
RUN apt-get update
RUN apt-get -qq install -y oracle-java8-installer

RUN \
    echo 'export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre' >> /kb/deployment/user-env.sh && \
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /kb/deployment/user-env.sh

# Install InterProScan
# RUN \
#     echo 'Downloading big interproscan file...' && \
#     wget -nv ftp://ftp.ebi.ac.uk/pub/software/unix/iprscan/5/5.18-57.0/interproscan-5.18-57.0-64-bit.tar.gz && \
#     tar xf interproscan-5.18-57.0-64-bit.tar.gz && \
#     mv interproscan-5.18-57.0 /kb/deployment/interproscan && \
#     echo 'export INTERPROSCAN_INSTALL=/kb/deployment/interproscan' >> /kb/deployment/user-env.sh && \
#     echo 'export PATH=$INTERPROSCAN_INSTALL:$PATH' >> /kb/deployment/user-env.sh


# Install InterProScan without data/ directory
RUN \
    echo 'Downloading interproscan tarball without data/...' && \
    curl -s http://bioseed.mcs.anl.gov/~fangfang/kb/interproscan-5.18-57.0-wo-data.tgz |tar xzf - && \
    mv interproscan-5.18-57.0 /kb/deployment/interproscan && \
    ln -s /data/interproscan-5.18-57.0-data /kb/deployment/interproscan/data && \
    echo 'export INTERPROSCAN_INSTALL=/kb/deployment/interproscan' >> /kb/deployment/user-env.sh && \
    echo 'export PATH=$INTERPROSCAN_INSTALL:$PATH' >> /kb/deployment/user-env.sh


# Copy local wrapper files, and build

COPY ./ /kb/module
RUN mkdir -p /kb/module/work

WORKDIR /kb/module

RUN make

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
