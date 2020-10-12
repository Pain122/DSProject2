FROM python:3.8

USER root
WORKDIR storage

COPY . .
RUN rm -rf venv && \
    rm -rf .idea && \
    rm -rf dfs.egg-info && \
    mkdir -p /var/storage && \
    python3 -m venv venv && \
    venv/bin/python -m pip install --upgrade pip && \
    venv/bin/pip install --upgrade setuptools pip && \
    venv/bin/pip install -r requirements.txt


ENTRYPOINT ["./boot_storage_node.sh"]
