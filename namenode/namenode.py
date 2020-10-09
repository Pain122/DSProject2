from flask import Flask, request
from . import database as db
from werkzeug.exceptions import BadRequest
from fastapi import HTTPException

from typing import Optional

from fastapi import FastAPI
from fastapi.requests import Request
from utils.serialize.namenode import *


# app = Flask(__name__)



# def check_request_data(data):
#     if data is None:
#         raise BadRequest()

app = FastAPI()

@app.get('/dfs_init', response_model=InitResponse)
async def init():
    # size = db.get_available_size()
    return

@app.post('/new_node', response_model=AddNodeResponse)
async def add_new_node(node: AddNodeRequest, request:Request):
    # new_id = db.add_node(request.client, node.available_storage)
    return

@app.post('/dfs_file_create', response_model=FileModel)
async def file_create(file: frmf('sas')):
    # db.create_file(file.path)
    return

@app.post('/dfs_file_read', response_model=FileModel)
async def file_read(file: frmf('sos')):
    """
    TODO: add checking
    """
    # node = db.find_node_by_file(file.path)
    return

@app.post('/dfs_file_write', response_model=FileModel)
async def file_write(file: frmf('ses', size=True)):
    # ip = db.write_file(file)
    return

@app.post('/dfs_file_delete', response_model=FileModel)
async def file_delete(file: frmf('sus')):
    # ip = db.delete_file(file)
    return

@app.post('/dfs_file_info', response_model=FileModel)
async def file_info(file: frmf('sqs')):
    # file_info = db.get_file_info(filename)
    return

@app.post('/dfs_file_copy', response_model=FileModel)
async def file_copy(file: frmf('sws', new_path=True)):
    # filename = data['filename']
    # new_filename = data['cp_filename']
    # db.copy_file(filename, new_filename)
    return FileModel()


@app.post('/dfs_file_move', response_model=FileModel)
async def file_move(file: frmf('srs', new_path=True)):
    # filename = data['filename']
    # new_filename = data['mv_filename']
    # db.move_file(filename, new_filename)
    return


@app.post('/dfs_read_directory', response_model=DirectoryModel)
async def read_directory(dir: DirectoryRequestModel):
    return


@app.post('/dfs_make_directory', response_model=DirectoryModel)
async def make_directory(dir: DirectoryRequestModel):
    return

@app.post('/dfs_delete_directory', response_model=DirectoryModel)
async def delete_directory(dir: DirectoryRequestModel):
    return
