from fastapi import HTTPException
from config import *


class NoSuchDirectory(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NO_SUCH_DIRECTORY, detail=NO_SUCH_DIRECTORY)


class NotEnoughStorage(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NOT_ENOUGH_STORAGE, detail=NOT_ENOUGH_STORAGE)


class NoNodeAvailable(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NO_NODE_AVAILABLE, detail=NO_NODE_AVAILABLE)


class NotEmptyDirectory(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NOT_EMPTY_DIRECTORY, detail=NOT_EMPTY_DIRECTORY)


class PathIsDirectory(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_PATH_IS_DIRECTORY, detail=PATH_IS_DIRECTORY)


class NodeDisconnected(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NODE_DISCONNECTED, detail=NODE_DISCONNECTED)


class FileNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_FILE_NOT_FOUND, detail=FILE_NOT_FOUND)


class IntegrityError(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_INTEGRITY_ERROR, detail=INTEGRITY_ERROR)


class FileExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_FILE_EXISTS, detail=FILE_EXISTS)
