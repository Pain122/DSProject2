from fastapi.requests import Request
from utils.serialize.namenode import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from namenode.database import *
from namenode.storage_conn import *
from uuid import uuid4
from namenode.exceptions import *
import os
from typing import Dict
import uvicorn

app = FastAPI()

Base.metadata.bind = db_engine
Base.metadata.drop_all()
Base.metadata.create_all()
Directory.create('/')

origins = [
    "http://localhost*",
    "http://localhost:8080*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_config=log_config)


# @app.on_event("startup")
# async def startup_event():
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
#     logger.addHandler(handler)


@app.post('/dfs_init', response_model=InitResponse)
async def init():
    db_init()
    send_init_all()
    storage_list = Node.get_node_models()
    resp = InitResponse(size=storage_list.available_size())
    return resp


@app.post('/new_node', response_model=AddNodeResponse)
async def add_new_node(node: AddNodeRequest, request: Request):
    if Node.q().filter(Node.storage_ip == request.client.host).count() == 0:
        storage_id = str(uuid4())
        print()
        model = StorageModel(storage_id=storage_id, storage_ip=request.client.host, available_size=node.available_storage)
        Node.create(model)
    else:
        node = Node.q().filter(Node.storage_ip == request.client.host).scalar()
        storage_id = node.storage_id
        logger.info(f'Node {node.storage_id} up!')
        paths = node.up()
        if paths is not None:
            for path in paths:
                post(node.storage_ip, 'delete', Status, json={'path': path})
    return AddNodeResponse(storage_id=storage_id)


@app.post('/dfs_file_create', response_model=FileModel)
async def file_create(file: frmf('FileCreateRequest')):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        raise NoSuchDirectory()
    if Directory.exist(file.path):
        raise PathIsDirectory()
    resp = create_file(file)
    return resp


@app.post('/dfs_file_read', response_model=FileModel)
async def file_read(file: frmf('FileReadRequest')):
    """
    TODO: add checking
    """
    ping_n_repl()
    file_obj = File.query_by_paths(file.path).scalar()
    if file_obj is None:
        raise FileNotFound()
    resp = FileModel.from_orm(file_obj)
    resp.storages = ping_all(resp.storages)
    if len(resp.storages) == 0:
        raise NodeDisconnected()
    return resp


@app.post('/dfs_file_write', response_model=FileModel)
async def file_write(file: frmf('FileWriteRequest', size=True)):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        raise NoSuchDirectory()
    resp = write_file(file)
    return resp


@app.post('/dfs_file_delete', response_model=FileModel)
async def file_delete(file: frmf('FileDeleteRequest')):
    ping_n_repl()
    if not File.exists(file.path):
        raise FileNotFound()
    resp = delete_file(file)
    return resp


@app.post('/dfs_file_info', response_model=FileModel)
async def file_info(file: frmf('FileInfoRequest')):
    ping_n_repl()
    if not File.exists(file.path):
        raise FileNotFound()
    file_obj = File.query_by_paths(file.path).scalar()
    return FileModel.from_orm(file_obj)


@app.post('/dfs_file_copy', response_model=FileModel)
async def file_copy(file: frmf('FileCopyRequest', new_path=True)):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        raise NoSuchDirectory()
    resp = copy_file(file)
    return resp


@app.post('/dfs_file_move', response_model=FileModel)
async def file_move(file: frmf('FileMoveRequest', new_path=True)):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        raise NoSuchDirectory()
    resp = move_file(file)
    return resp


@app.post('/dfs_read_directory', response_model=DirectoryModel)
async def read_directory(dir: DirectoryRequestModel):
    ping_n_repl()
    if not Directory.exist(dir.path):
        raise NoSuchDirectory()
    resp = get_dir_model(dir.path)
    return resp


@app.post('/dfs_make_directory', response_model=DirectoryModel)
async def make_directory(dir: DirectoryRequestModel):
    ping_n_repl()
    if Directory.exist(dir.path):
        raise NoSuchDirectory()
    Directory.create(dir.path)
    resp = DirectoryModel(storages=[], files=[], path=dir.path)
    return resp


@app.post('/dfs_delete_directory', response_model=DirectoryModel)
async def delete_directory(dir: DirectoryRequestModel):
    if not Directory.exist(dir.path):
        raise NoSuchDirectory()
    if File.query_by_dir(dir.path).count() > 0 or Directory.q().filter(Directory.path.startswith(dir.path)).count() > 1:
        raise NotEmptyDirectory()
    resp = get_dir_model(dir.path)
    Directory.delete(dir.path)
    return resp
