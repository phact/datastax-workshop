FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    git git-core python-pip python-setuptools python-dev build-essential
RUN git clone https://github.com/slowenthal/cql_kernel/
RUN apt-get install libev4 libev-dev
RUN pip install --upgrade cassandra-driver 

COPY config.txt config.txt

RUN mkdir ~/.jupyter
COPY jupyter_notebook_config.py jupyter_notebook_config.py

RUN sed -i "s/localhost/$(sed 's:/:\\/:g' config.txt)/" cql_kernel/cql_kernel/install.py

COPY config.txt cql_kernel/cql_kernel/config.txt

RUN pip install jupyter

COPY data/populate_simple.py .
COPY data/populate.py .
COPY data/metadata_10k.json .
COPY data/geodata.csv .

RUN mkdir notebooks
COPY notebooks notebooks

RUN /sbin/ip route
RUN echo "if you error out after this, you didn't set up config.txt right and/or your rpc_address needs to change"
#RUN python populate_simple.py metadata_10k.json geodata.csv

#RUN python populate.py metadata_10k.json geodata.csv

RUN cd cql_kernel/cql_kernel &&  python install.py $(< ../../config.txt)
RUN cd cql_kernel && python setup.py install

ENTRYPOINT jupyter notebook --no-browser --port 7001 --ip=* --notebook_dir="notebooks"  
#ENTRYPOINT /bin/bash
