from fastapi import HTTPException
from config import *


class NodeDisconnected(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NODE_DISCONNECTED)


class FileNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_FILE_NOT_FOUND)


class NoSuchDirectory(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NO_SUCH_DIRECTORY)


class NotEnoughStorage(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NOT_ENOUGH_STORAGE)


class NoNodeAvailable(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NO_NODE_AVAILABLE)


class NotEmptyDirectory(HTTPException):
    def __init__(self):
        super().__init__(status_code=CODE_NOT_EMPTY_DIRECTORY)