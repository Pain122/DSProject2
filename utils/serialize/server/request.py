from pydantic import BaseModel, create_model

class CreateFile(BaseModel):
    path = str
    file =''