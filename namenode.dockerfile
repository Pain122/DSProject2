FROM python:3.8

USER root
WORKDIR namenode

COPY . .
RUN rm -rf venv && \
    rm -rf .idea && \
    rm -rf dfs.egg-info && \
    python3 -m venv venv && \
    venv/bin/python -m pip install --upgrade pip && \
    venv/bin/pip install --upgrade setuptools pip && \
    venv/bin/pip install -r requirements.txt

ENV DB_ADDR db:5432
ENV DB_LOGIN nikitasmirnov
ENV DB_PASS yanikitasmirnov
ENV DB_NAME test
ENTRYPOINT ["./boot_namenode.sh"]
