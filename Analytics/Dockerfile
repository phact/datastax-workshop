FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    git git-core python-pip python-setuptools python-dev build-essential wget software-properties-common
RUN wget https://github.com/phact/spark-kernel/releases/download/v0.1.6-cassandra/kernel-0.1.6.0-cassandra-SNAPSHOT.tgz
RUN tar -xvf kernel-0.1.6.0-cassandra-SNAPSHOT.tgz
RUN apt-get install libev4 libev-dev

COPY config.txt config.txt

RUN mkdir ~/.jupyter
COPY jupyter_notebook_config.py jupyter_notebook_config.py

COPY config.txt config.txt

RUN pip install jupyter

RUN mkdir analytics_notebooks
COPY analytics_notebooks analytics_notebooks

RUN /sbin/ip route
RUN echo "if you error out after this, you didn't set up config.txt right and/or your rpc_address needs to change"

RUN kernel-0.1.6.0-cassandra-SNAPSHOT/bin/setup.sh $(< ../../config.txt)

#have to install DSE binaries locally to be able to run the spark notebook
RUN wget http://sebastian.estevez%40datastax.com:Testing123@eap-downloads.datastax.com/dse/5.0.0-rc1/tar/enterprise/dse-5.0.0-bin.tar.gz
RUN tar -xvf dse-5.0.0-bin.tar.gz

RUN \
  echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
  add-apt-repository -y ppa:webupd8team/java && \
  apt-get update && \
  apt-get install -y oracle-java8-installer && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/cache/oracle-jdk8-installer

ENV JAVA_HOME /usr/lib/jvm/java-8-oracle


#ENTRYPOINT export PATH="dse-5.0.0/bin:$PATH" && jupyter notebook --no-browser --port 7001 --ip=* --notebook_dir="analytics_notebooks"  
ENTRYPOINT export PATH="dse-5.0.0/bin:$PATH" && /bin/bash
