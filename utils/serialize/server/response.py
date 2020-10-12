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

    @classmethod
    def init(cls, ok: bool, path: str, storage_id: str):
        if ok:
            status = Status.default()
        else:
            status = Status(status='error')

        return cls(status=status, path=path, storage_id=storage_id)


