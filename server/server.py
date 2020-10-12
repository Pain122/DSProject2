import os
import posixpath

import psutil
import requests
from pydantic.error_wrappers import ValidationError

from config import *
from .exceptions import DirDoesNotExist
from utils.serialize.server import *
import uvicorn
import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def post(ip, uri, data, model, js=True):
    try:
        url = posixpath.join(ip, uri)
        if js:
            x = requests.post(url, json=data)
        else:
            x = requests.post(url, file=data)
        try:
            x_data = model.parse_raw(x.content)
            return x_data, 200
        except ValidationError:
            return None, CODE_CORRUPTED_RESPONSE
    except requests.exceptions.ConnectionError:
        return None, CODE_CONNECTION_ERROR


class Server:
    def __init__(self, server_ip, working_dir=os.getcwd()):
        ###
        # server_ip: String; NameNode ip address
        ###
        if not os.path.isdir(working_dir):
            raise DirDoesNotExist()
        self.working_dir = working_dir
        self.server_ip = server_ip
        self.id = 0
        self.connected = False
        self.connect_to_server()

    def connect_to_server(self):
        data = AddNodeRequest(available_storage=psutil.disk_usage('/').free, port=find_free_port())
        self.port = data.port
        resp, code = post(NAME_NODE_ADDRESS, 'new_node', data.dict(), AddNodeResponse)
        if code == 200:
            self.id = resp.storage_id
            self.connected = True
            print('Connection Successful! Node id:' + str(resp.storage_id))
        else:
            print('Connection failed')
