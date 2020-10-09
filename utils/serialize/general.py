from pydantic import BaseModel
from typing import List
from os import path


class StorageModel(BaseModel):
    storage_id: int
    storage_ip: str
    available_size: int

    class Config:
        orm_mode = True

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


class DirectoryModel(BaseFileModel):

    files: List[FileModel]

    def _files(self):
        return [path.dirname(file.path) for file in self.files]