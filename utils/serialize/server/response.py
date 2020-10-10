from pydantic import BaseModel


class Status(BaseModel):
    status: str

    @classmethod
    def default(cls):
        return cls(status='ok')


class FileReport(BaseModel):
    status: Status
    storage_id: str
    path: str

    def __init__(self, ok: bool, path: str, storage_id: str):
        if ok:
            status = Status.default()
        else:
            status = Status(status='error')

        super().__init__(status=status, path=path, storage_id=storage_id)


