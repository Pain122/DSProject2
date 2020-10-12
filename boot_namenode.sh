#!/bin/sh
# shellcheck disable=SC2039
. venv/bin/activate
uvicorn namenode.app:app --reload --host 0.0.0.0