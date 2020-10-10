import os
import posixpath

import psutil
import requests
from pydantic.error_wrappers import ValidationError

from config import NAME_NODE_ADDRESS, CODE_CORRUPTED_RESPONSE, CODE_CONNECTION_ERROR
from server.exceptions import DirDoesNotExist
from utils.serialize.server import *


def post(ip, uri, data, model, js=True):
    try:
        url = posixpath.join(ip, uri)
        if js:
            x = requests.post(f'http://{ip}/' + uri, json=data)
        else:
            x = requests.post(f'http://{ip}/' + uri, file=data)
        try:
            x_data = model.parse_raw(x.content)
            return x_data
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

    def connect_to_server(self):
        data = AddNodeRequest(available_storage=psutil.disk_usage('/').free)
        resp = post(NAME_NODE_ADDRESS, '/new_node', data.dict(), AddNodeResponse)
        self.id = resp.storage_id
        print('Connection Successful! Node id:' + str(resp.json()['id']))
