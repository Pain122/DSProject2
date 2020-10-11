from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile
from fastapi.params import File as FileForm, Form
from config import *
from server.server import Server
import sys
from shutil import copyfile
from werkzeug.exceptions import BadRequest
from server.exceptions import IntegrityError, ServerConnectionError
from utils.serialize.namenode import frmf
from utils.serialize.server.response import Status, FileReport
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from .dbconn import *


def check_file(path: str, file_path: str, folder_path: str):
    if query_file(path):
        rm_file_folders(file_path, folder_path)


def create(file_path: str, folder_path: str, file: UploadFile):
    if not os.path.isfile(file_path):

        check_create_dirs(folder_path)

        with open(file_path, 'ab') as f:
            for chunk in iter(lambda: file.file.read(10000), b''):
                f.write(chunk)

            f.close()


def report(file_path: str):
    if not DEBUG:
        rep = FileReport(True, file_path, srv.id)
        requests.post('http://' + NAME_NODE_ADDRESS + '/report', rep)


def replica(file_path: str, path: str, storage_ips: str):
    mp_encoder = MultipartEncoder(
        fields={
            'path': path,
            'file': ('None', open(file_path, 'rb'), 'text/plain'),
        }
    )
    for storage_ip in storage_ips:
        requests.post(
            'http://' + storage_ip + '/create',
            data=mp_encoder,
            headers={'Content-Type': mp_encoder.content_type}
        )
    return True


def iterate_path(path: str):
    working_length = len(WORKING_DIR.split(os.path.sep))
    return os.path.join(WORKING_DIR, *path.split(os.path.sep)[working_length:-1])


def make_file_path(path: str):
    return os.path.join(WORKING_DIR, *path.split('/'))


def make_dirs_path(path: str):
    return os.path.join(WORKING_DIR, *path.split('/')[:-1])


def check_create_dirs(dir_path: str):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def rm_file_folders(fl_path: str, fd_path: str):
    os.remove(fl_path)
    fold_path = fd_path

    while (fold_path != WORKING_DIR) and (len(os.listdir(fold_path)) == 0):
        os.rmdir(fold_path)
        fold_path = iterate_path(fold_path)


def check_req(data):
    if data is None:
        raise BadRequest()


srv = Server(NAME_NODE_ADDRESS)
srv.connect_to_server()
if not srv.connected and not DEBUG:
    print(srv)
    raise ServerConnectionError

app = FastAPI()


@app.get('/ping')
async def ping():
    return Status.default()


@app.post('/create')
async def create_file(path: str = Form(...), file: UploadFile = FileForm(...)):
    file_path = make_file_path(path)
    folder_path = make_dirs_path(path)

    if not os.path.isfile(file_path):

        create(file_path, folder_path, file)
        report(file_path)

        if check_file(path, file_path, folder_path):
            storages = query_storage(srv.id, path)
            replica(file_path, path, storages)

        return Status.default()
    else:
        raise IntegrityError


@app.post('/create_replica')
async def create_replica(path: str = Form(...), file: UploadFile = FileForm(...)):
    file_path = make_file_path(path)
    folder_path = make_dirs_path(path)

    if not os.path.isfile(file_path):

        create(file_path, folder_path, file)
        report(file_path)

        if query_file(path):
            rm_file_folders(file_path, folder_path)

        check_file(path, file_path, folder_path)

        return Status.default()
    else:
        raise IntegrityError


@app.post('/delete')
async def delete_file(file: frmf('DeleteModel')):
    file_path = make_file_path(file.path)
    folder_path = make_dirs_path(file.path)

    if os.path.isfile(file_path):
        rm_file_folders(file_path, folder_path)
        return Status.default()
    else:
        raise IntegrityError


@app.post('/copy')
async def copy(path: frmf('CopyModel', new_path=True)):
    file_path = make_file_path(path.path)
    new_file_path = make_file_path(path.new_path)
    new_folder_path = make_dirs_path(path.new_path)

    if not (os.path.isfile(file_path) and not os.path.isfile(new_file_path)):
        check_create_dirs(new_folder_path)
        copyfile(file_path, new_file_path)
        check_file(path.new_path, new_file_path, new_folder_path)
        return Status.default()
    else:
        raise IntegrityError()


@app.post('/move')
async def move(path: frmf('MoveModel', new_path=True)):
    file_path = make_file_path(path.path)
    new_file_path = make_file_path(path.new_path)
    folder_path = make_dirs_path(path.path)
    new_folder_path = make_dirs_path(path.new_path)

    if os.path.isfile(file_path) and not os.path.isfile(new_file_path):
        check_create_dirs(new_folder_path)
        copyfile(file_path, new_file_path)
        rm_file_folders(file_path, folder_path)
        check_file(path.new_path, new_file_path, new_folder_path)
        return Status.default()
    else:
        raise IntegrityError()


@app.post('/send')
async def send(path: str):
    file_path = make_file_path(path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        raise IntegrityError()


@app.get('/ping')
async def ping():
    return Status.default()


@app.post('/replicate')
async def replicate(files: List[FileModel]):
    for file_model in files:
        file_path = make_file_path(file_model.path)
        if os.path.isfile(file_path):
            for serv in file_model.storages:
                replica(file_path, file_model.path, serv.storage_ip)
        else:
            raise IntegrityError

    return Status.default()
