# TODO unite all the exception classes to a single file
from fastapi import FastAPI
import os
from server.server import Server
import sys
from flask import send_from_directory, abort
from shutil import copyfile
from werkzeug.exceptions import BadRequest
from server.exceptions import IntegrityError, FileNotFound, ServerConnectionError


def check_req(data):
    if data is None:
        raise BadRequest()


srv = Server(sys.argv[1])

if not srv.connected:
    raise ServerConnectionError

app = FastAPI()

# # The absolute path of the directory containing CSV files for users to download
# app.config["DFS"] = srv.working_dir


@app.post('/rcv')
async def create_file():
    data = request.get_json()
    check_req(data)
    if not os.path.exists(data['path']):
        path = os.path.join(srv.working_dir, data['path'])
        file = open(path)
        file.write(data['file'])
        file.close()
        return {'status': 'ok'}
    else:
        raise IntegrityError()


@app.post('/upd')
async def update_file():
    data = request.get_json()
    if data is None:
        return {'error': 'Bad request'}, 400
    else:
        data = request.get_json()
        if os.path.exists(data['path']):
            os.remove(data['path'])
            file = open(data['path'])
            file.write(data['file'])
            file.close()
            return {'status': 'OK'}
        else:
            raise FileNotFound()


@app.post('/send')
async def send():
    data = request.get_json()
    if data is None:
        return {'error': 'Bad request'}, 400
    else:
        filename = request['file']
        try:
            return send_from_directory(app.config['DFS'], filename=filename, as_attachment=True)
        except FileNotFoundError:
            abort(404)


@app.post('/delete')
async def delete():
    data = request.get_json()
    if data is None:
        return {'error': 'Bad request'}, 400
    else:
        if os.path.exists(data['path']):
            os.remove(data['path'])
            return {'status': 'OK'}
        else:
            raise FileNotFound()


@app.post('/empty')
async def create_file():
    data = request.get_json()
    check_req(data)
    if not os.path.exists(data['path']):
        path = os.path.join(srv.working_dir, data['path'])
        file = open(path)
        file.close()
        return {'status': 'OK'}
    else:
        raise IntegrityError()


@app.post('/copy')
async def copy():
    data = request.get_json()
    check_req(data)
    if not (os.path.exists(data['path']) and os.path.exists(data['copy_path'])):
        copyfile(data['path'], data['copy_path'])
        return {'status': 'OK'}
    else:
        raise IntegrityError()


@app.post('/move')
async def move():
    data = request.get_json()
    check_req(data)
    if not (os.path.exists(data['path']) and os.path.exists(data['copy_path'])):
        copyfile(data['path'], data['copy_path'])
        os.remove(data['path'])
        return {'status': 'OK'}
    else:
        raise IntegrityError()


@app.post('/mkdir')
async def mkdir():
    data = request.get_json()
    check_req(data)
    try:
        os.mkdir(data['path'])
        return {'status': 'OK'}
    except OSError:
        raise IntegrityError()


@app.post('/rmdir')
async def rmdir():
    data = request.get_json()
    check_req(data)
    try:
        os.rmdir(data['path'])
        return {'status': 'OK'}
    except OSError:
        raise IntegrityError()


@app.post('/ping', methods=['GET'])
async def ping():
    return {'status': 'OK'}
