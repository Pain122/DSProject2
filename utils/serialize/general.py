from pydantic import BaseModel, conlist
from typing import List, Type, Any, Optional
import os
from uuid import uuid4, UUID


class StorageModel(BaseModel):
    storage_id: str
    storage_ip: str
    available_size: int

    class Config:
        orm_mode = True

    def __init__(self, *args, **kwargs):
        if kwargs.get('storage_id', None) is None:
            kwargs['storage_id'] = str(uuid4())
        elif isinstance(kwargs['storage_id'], UUID):
            kwargs['storage_id'] = str(kwargs['storage_id'])
        super().__init__(*args, **kwargs)


class StorageListModel(BaseModel):

    storages: List[StorageModel]

    def available_size(self):
        res = 0
        for storage in self.storages:
            res += storage.available_size
        return res


class BaseFileModel(BaseModel):
    storages: List[StorageModel]
    path: str

    def available_size(self):
        res = 0
        for storage in self.storages:
            res += storage.available_size
        return res


class FileModel(BaseFileModel):
    size: int

    class Config:
        orm_mode = True


class SimpleFileModel(BaseModel):
    path: str

    class Config:
        orm_mode = True


class DirectoryModel(BaseFileModel):

    files: List[SimpleFileModel]

    def _files(self):
        return [os.path.dirname(file.path) for file in self.files]





