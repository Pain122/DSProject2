from pydantic import BaseModel


class Status(BaseModel):
    status: str

    @classmethod
    def default(cls):
        return cls(status='ok')


class FileReport(BaseModel):
    status: Status
    is_replica: bool
    path: str

    def __init__(self, ok: bool, path: str, is_replica: bool):
        if ok:
            status = Status.default()
        else:
            status = Status(status='error')

        super().__init__(status=status, path=path, is_replica=is_replica)


