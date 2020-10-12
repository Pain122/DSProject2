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

RUN chmod 777 ./boot_namenode.sh
ENTRYPOINT ["./boot_namenode.sh"]
