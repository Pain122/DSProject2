from starlette.responses import FileResponse
from fastapi import FastAPI, UploadFile
import os
from fastapi.params import File, Form
from config import DEBUG, WORKING_DIR
from server.server import Server, FileModel, post
import sys
from shutil import copyfile
from werkzeug.exceptions import BadRequest
from server.exceptions import IntegrityError, ServerConnectionError
from utils.serialize.server.response import Status
from typing import List


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


srv = Server(sys.argv[1])

if not srv.connected and not DEBUG:
    raise ServerConnectionError

app = FastAPI()


@app.get('/ping')
async def ping():
    return Status.default()


@app.post('/create')
async def create_file(path: str = Form(...), file: UploadFile = File(...)):
    file_path = make_file_path(path)
    folder_path = make_dirs_path(path)

    if not os.path.isfile(file_path):

        check_create_dirs(folder_path)

        with open(file_path, 'ab') as f:
            for chunk in iter(lambda: file.file.read(10000), b''):
                f.write(chunk)

            f.close()

        return Status.default()
    else:
        raise IntegrityError


@app.post('/delete')
async def delete_file(path: str = Form(...)):
    file_path = make_file_path(path)
    folder_path = make_dirs_path(path)

    if os.path.isfile(file_path):
        rm_file_folders(file_path, folder_path)
        return Status.default()
    else:
        raise IntegrityError


@app.post('/replicate')
async def replicate(file: List[FileModel]):
    for storage in file.storages:
        f = open(WORKING_DIR + file.path, 'rb')
        post(storage.storage_ip, '/crt', f, File(...), False)
    return Status.default()


@app.post('/copy')
async def copy(path: str = Form(...), new_path: str = Form(...)):
    file_path = make_file_path(path)
    new_file_path = make_file_path(new_path)
    folder_path = make_dirs_path(new_path)

    if not (os.path.isfile(path) and not os.path.isfile(new_path)):
        check_create_dirs(folder_path)
        copyfile(file_path, new_file_path)
        return Status.default()
    else:
        raise IntegrityError()


@app.post('/move')
async def move(path: str = Form(...), new_path: str = Form(...)):
    file_path = make_file_path(path)
    new_file_path = make_file_path(new_path)
    folder_path = make_dirs_path(path)
    new_folder_path = make_dirs_path(new_path)

    if os.path.isfile(file_path) and not os.path.isfile(new_file_path):
        check_create_dirs(new_folder_path)
        copyfile(file_path, new_file_path)
        rm_file_folders(file_path, folder_path)
        return Status.default()
    else:
        raise IntegrityError()


@app.post('/send')
async def send(path: str = Form(...)):
    file_path = make_file_path(path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        raise IntegrityError()


@app.get('/ping')
async def ping():
    return Status.default()
