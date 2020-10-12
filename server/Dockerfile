FROM python:3.8

USER root
WORKDIR storage_node


COPY . .
COPY requirements.txt requirements.txt
RUN python3 -m venv venv && \
    venv/bin/python -m pip install --upgrade pip && \
    venv/bin/pip install --upgrade setuptools pip && \
    venv/bin/pip install -r requirements.txt


ENV WORKING_DIR /var/storage
ENV NAMENODE_ADDR http://namenode:8000
ENV DB_ADDR db:5432
ENV DB_LOGIN nikitasmirnov
ENV DB_PASS yanikita
ENV DB_NAME test
ENTRYPOINT ["./boot.sh"]