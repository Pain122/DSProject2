from fastapi.requests import Request
from utils.serialize.namenode import *
from fastapi import FastAPI
from .database import *
from .storage_conn import *
from uuid import uuid4
import os

app = FastAPI()


@app.get('/dfs_init', response_model=InitResponse)
async def init():
    db_init()
    send_init_all()
    storage_list = Node.get_node_models()
    resp = InitResponse(available_size=storage_list.available_size())
    return resp


@app.post('/new_node', response_model=AddNodeResponse)
async def add_new_node(node: AddNodeRequest, request: Request):
    model = StorageModel(storage_id=uuid4(), storage_ip=request.client.host, available_size=node.available_storage)
    Node.create(model)
    return AddNodeResponse(storage_id=model.storage_id)


@app.post('/dfs_file_create', response_model=FileModel)
async def file_create(file: frmf('FileCreateRequest')):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        # TODO: add exception
        pass
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
        # TODO: add exception
        pass
    return FileModel.from_orm(file_obj)


@app.post('/dfs_file_write', response_model=FileModel)
async def file_write(file: frmf('FileWriteRequest', size=True)):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        # TODO: add exception
        pass
    resp = write_file(file)
    return resp


@app.post('/dfs_file_delete', response_model=FileModel)
async def file_delete(file: frmf('FileDeleteRequest')):
    ping_n_repl()
    if not File.exists(file.path):
        # TODO: add exception
        pass
    resp = delete_file(file)
    return resp


@app.post('/dfs_file_info', response_model=FileModel)
async def file_info(file: frmf('FileInfoRequest')):
    ping_n_repl()
    file_obj = File.query_by_paths(file.path).scalar()
    return FileModel.from_orm(file_obj)


@app.post('/dfs_file_copy', response_model=FileModel)
async def file_copy(file: frmf('FileCopyRequest', new_path=True)):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        # TODO: add exception
        pass
    resp = copy_file(file)
    return resp


@app.post('/dfs_file_move', response_model=FileModel)
async def file_move(file: frmf('FileMoveRequest', new_path=True)):
    ping_n_repl()
    if not Directory.exist(os.path.dirname(file.path)):
        # TODO: add exception
        pass
    resp = move_file(file)
    return resp


@app.post('/dfs_read_directory', response_model=DirectoryModel)
async def read_directory(dir: DirectoryRequestModel):
    ping_n_repl()
    if not Directory.exist(dir.path):
        # TODO: add exception
        pass
    resp = get_dir_model(dir.path)
    return resp


@app.post('/dfs_make_directory', response_model=DirectoryModel)
async def make_directory(dir: DirectoryRequestModel):
    ping_n_repl()
    if Directory.exist(dir.path):
        # TODO: add exception
        pass
    Directory.create(dir.path)
    resp = DirectoryModel(storages=[], files=[], path=dir.path)
    return resp

@app.post('/dfs_delete_directory', response_model=DirectoryModel)
async def delete_directory(dir: DirectoryRequestModel):
    if not Directory.exist(dir.path):
        # TODO: add exception
        pass
    if File.query_by_dir(dir.path).count() > 0 or Directory.q().filter(Directory.path.startswith(dir.path)).count() > 1:
        # TODO: add exception
        pass
    resp = get_dir_model(dir.path)
    Directory.delete(dir.path)
    return resp
