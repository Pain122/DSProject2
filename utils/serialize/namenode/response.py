from ..general import *
from pydantic import BaseModel
from typing import List


class InitResponse(BaseModel):
    size: int


class AddNodeResponse(BaseModel):
    storage_id: int
