from .database import Node
from utils.serialize.general import *
from utils.serialize.namenode import *


def url_wrapper(ip: str, port: int):
    return f'http://{ip}:{port}'


def post(url, uri, data, model: BaseModel) -> BaseModel:
    pass
    # url = join(url, uri)
    # try:
    #     x = r.post(url, json=data)
    #     try:
    #         return model.from_raw(x.content)
    #     except ValidationError:
    #         raise ServerError()
    # except r.exceptions.ConnectionError:
    #     raise NodeDisconnected()


def send_init(node_ip: str) -> None:
    pass


def send_init_all() -> None:
    ips = Node.q().values(Node.storage_ip)
    for ip in ips:
        send_init(ip)


def ping(node_ip: str) -> bool:
    pass


def replicate(node: Node, path: str = None) -> None:
    pass


def ping_n_repl() -> None:
    nodes = Node.q()
    for node in nodes:
        if not ping(node.storage_ip):
            replicate(node)


def create_file(file: frmf('FileCreateRequest')) -> FileModel:
    pass


def write_file(file: frmf('FileWriteRequest')) -> FileModel:
    pass


def delete_file(file: frmf('FileWriteRequest')) -> FileModel:
    pass


def copy_file(file: frmf('FileCopyRequest')) -> FileModel:
    pass


def move_file(file: frmf('FileMoveRequest')) -> FileModel:
    pass