from posixpath import join
import requests as r
from typing import Any
from config import NAME_NODE_ADDRESS, logger


def post(uri, **data) -> Any:
    url = join(NAME_NODE_ADDRESS, uri)
    logger.info(data)
    try:
        x = r.post(url, **data, timeout=1)
        logger.info(x.content)
    except r.exceptions.Timeout:
        pass
