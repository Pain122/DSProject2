from pydantic import BaseModel, create_model
from typing import List, Optional


class AddNodeRequest(BaseModel):
    available_storage: int
    port: int


class DirectoryRequestModel(BaseModel):
    path: str


def frmf(name='FileRequestModel', new_path: bool = False, size: bool = False):
    kwargs = {
        'path': (str, ...)
    }
    if new_path:
        kwargs['new_path'] = (str, ...)
    if size:
        kwargs['size'] = (int, ...)
    return create_model(name, **kwargs)
