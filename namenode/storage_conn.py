from namenode.database import *
from utils.serialize.general import *
from utils.serialize.namenode import *

def url_wrapper(ip: str, port: int):
    return f'http://{ip}:{port}'


def post(ip, uri, model: Any, **data) -> Any:
    url = join(url_wrapper(ip, 8001), uri)
    try:
        x = r.post(url, **data, timeout=1)
        return model.parse_raw(x.content)
    except r.exceptions.Timeout:
        raise NodeDisconnected()


def get(ip, uri, model: Any) -> Any:
    url = join(url_wrapper(ip, 8001), uri)
    try:
        x = r.get(url, timeout=1)
        return model.parse_raw(x.content)
    except r.exceptions.Timeout:
        raise NodeDisconnected()


def send_init(node_ip: str) -> None:
    pass


def send_init_all() -> None:
    ips = Node.q().values(Node.storage_ip)
    for ip in ips:
        send_init(ip)


def ping(node_ip: str) -> bool:
    try:
        logger.info(f'{type(Status)}')
        get(node_ip, 'ping', Status)
        return True
    except NodeDisconnected:
        return False
    pass


def replica(files: List[FileModel], node_ip: str) -> None:
    post(node_ip, 'replica', Status, json=[file.dict() for file in files])


def fall_node_replica(node: Node) -> None:
    send_mapping = node.fall()
    if send_mapping is not None:
        for node, files in send_mapping.items():
            replica(files, node.storage_ip)


def ping_n_repl() -> None:
    for node in Node.q():
        if not ping(node.storage_ip):
            replicate(node)


def empty_file(path: str) -> dict:
    mp_encoder = MultipartEncoder(
        fields={
            'path': path,
            'file': ('filename', io.BytesIO(b""), 'text/plain'),
        }
    )
    return {
        'data': mp_encoder,
        'headers': {'Content-Type': mp_encoder.content_type}
    }


def create_file(file: frmf('FileCreateRequest')) -> FileModel:
    pass


def write_file(file: frmf('FileWriteRequest')) -> FileModel:
    nodes = Node.get_sorted_nodes(size=file.size)
    if len(nodes) == 0:
        raise NotEnoughStorage()
    main_send, repl_send = main_replica_split(nodes)
    if File.exists(file.path):
        raise FileExists()
    PendingFileNode.add_tasks({node.storage_ip: [file.path] for node in main_send + repl_send})
    return FileModel(storages=main_send + repl_send, path=file.path, size=file.size)


def delete_file(file: frmf('FileDeleteRequest')) -> FileModel:
    q = FileNode.q().filter(FileNode.path == file.path)
    subq = q.subquery()
    nodes = Node.q().filter(Node.active==True).join(subq, Node.storage_id == subq.c.storage_id).all()
    q.delete(synchronize_session='fetch')
    session.commit()
    for node in nodes:
        post(node.ip, 'delete', Status, json=file.dict())
    return FileModel.from_orm(File.query_by_paths(file.path).scalar())


def copy_file(file: frmf('FileCopyRequest', new_path=True)) -> FileModel:
    if File.exists(file.new_path):
        raise FileExists()
    file_obj = File.query_by_paths(file.path).scalar()
    nodes = [node for node in file_obj.storages if node.available_size > file_obj.size]
    new_file_obj = File.create(path=file.new_path, size=file_obj.size)
    for node in nodes:
        st = post(node.storage_ip, 'copy', Status, json=file.dict())
        if st == Status.default():
            new_file_obj.storages.append(node)
    session.commit()
    return FileModel.from_orm(new_file_obj)


def move_file(file: frmf('FileMoveRequest')) -> FileModel:
    if File.exists(file.new_path):
        raise FileExists()
    file_obj = File.query_by_paths(file.path).scalar()
    nodes = [node for node in file_obj.storages if node.available_size > file_obj.size]
    new_file_obj = File.create(path=file.new_path, size=file_obj.size)
    for node in nodes:
        st = post(node.storage_ip, 'copy', Status, json=file.dict())
        if st == Status.default():
            new_file_obj.storages.append(node)
    session.delete(file_obj)
    for storage in new_file_obj.storages:
        storage.available_size += new_file_obj.size
    session.commit()
    return FileModel.from_orm(new_file_obj)