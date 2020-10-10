from fastapi.params import File
from pydantic import BaseModel


class CreateFile(BaseModel):
    path = str
    file = File(...)
