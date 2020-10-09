import posixpath

import requests
import psutil
import os

from pydantic.error_wrappers import ValidationError

from config import NAME_NODE_ADDRESS
from server.exceptions import DirDoesNotExist
from utils.serialize.general import StorageModel
from utils.serialize.namenode import *
from client.client import post, CODE_CORRUPTED_RESPONSE, CODE_CONNECTION_ERROR


class Server:
    def __init__(self, server_ip, working_dir=os.getcwd()):
        ###
        # server_ip: String; NameNode ip address
        # files_per_dir: Integer; Number of files allowed per directory
        ###
        if not os.path.isdir(working_dir):
            raise DirDoesNotExist()
        self.working_dir = working_dir
        self.server_ip = server_ip
        self.id = 0
        self.connected = False

    def post(self, uri, data, model):
        try:
            url = posixpath.join(NAME_NODE_ADDRESS, uri)
            x = requests.post(url, json=data)
            try:
                x_data = dict(model.parse_raw(x.content))
                return x_data, x.status_code
            except ValidationError:
                return None, CODE_CORRUPTED_RESPONSE
        except requests.exceptions.ConnectionError:
            return None, CODE_CONNECTION_ERROR

#     def connect_to_server(self):
#         data = {'size': psutil.disk_usage('/').free}
#         self.post('/new_node', data, AddNodeResponse)
#         resp = requests.get('https://' + self.server_ip + '/new_node/', data)
#         try:
#             resp = requests.get('https://' + self.server_ip + '/new_node/', data)
#             self.connected = True
#             self.id = AddNodeResponse.parse_raw(resp.content)
#             print('Connection Successful! Node id:' + str(resp.json()['id']))
#         exc:
#             return {'error': 'Could not connect to the NameNode'}
#
# AddNodeResponse.parse_raw(resp.content)