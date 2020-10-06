import requests
import os
from pydantic.error_wrappers import ValidationError
from utils.serialize import *
from config import NAME_NODE_ADDRESS

CONNECTION_ERROR = 'Connection with server is lost!'
CORRUPTED_RESPONSE = 'The response from server is corrupted!'
NO_NODE_AVAILABLE = 'No nodes are available to store this file!'
NOT_ENOUGH_STORAGE = 'There is not enough memory to store your file!'
NODE_DISCONNECTED = 'Node storing the file disconnected!'
FILE_NOT_FOUND = 'File with such name was not found!'
NO_SUCH_DIRECTORY = 'Directory with such name doesn\'t exist!'
INTEGRITY_ERROR = 'One of the storage servers reported an integrity error!'

CODE_CONNECTION_ERROR = 418
CODE_CORRUPTED_RESPONSE = 500
CODE_NO_NODE_AVAILABLE = 501
CODE_NOT_ENOUGH_STORAGE = 502
CODE_NODE_DISCONNECTED = 503
CODE_FILE_NOT_FOUND = 504
CODE_NO_SUCH_DIRECTORY = 505
CODE_INTEGRITY_ERROR = 506

error_dict = {
    CODE_CORRUPTED_RESPONSE: CORRUPTED_RESPONSE,
    CODE_CONNECTION_ERROR: CONNECTION_ERROR,
    CODE_NO_NODE_AVAILABLE: NO_NODE_AVAILABLE,
    CODE_NOT_ENOUGH_STORAGE: NOT_ENOUGH_STORAGE,
    CODE_NODE_DISCONNECTED: NODE_DISCONNECTED,
    CODE_FILE_NOT_FOUND: FILE_NOT_FOUND,
    CODE_NO_SUCH_DIRECTORY: NO_SUCH_DIRECTORY,
    CODE_INTEGRITY_ERROR: INTEGRITY_ERROR
}

cmd_model_map = {
    'dfs_init': StorageModel,
    'dfs_file_create': FileModel,
    'dfs_file_read': FileModel,
    'dfs_file_write': FileModel,
    'dfs_file_delete': FileModel,
    'dfs_file_move': FileModel,
    'dfs_file_copy': FileModel,
    'dfs_file_info': FileModel,
    'dfs_dir_open': DirectoryModel,
    'dfs_dir_make': DirectoryModel,
    'dfs_dir_delete': DirectoryModel,
    'dfs_dir_read': DirectoryModel,
}


def name_error_handler(func):
    def wrapper(*args):
        metadata = args[1]
        cmd, console_data = metadata['cmd'], metadata['console_data']
        uri = os.path.join(NAME_NODE_ADDRESS, cmd)
        model = cmd_model_map[cmd]
        response, code = post(uri, console_data, model)
        if response_failed(code):
            return fetch_error_msg(code)
        else:
            data = {
                'console_data': console_data,
                'response': response
            }
            return func(args[0], data)

    return wrapper


def storage_error_handler(func):
    def wrapper(*args):
        metadata = args[1]
        cmd, address, data = metadata['cmd'], metadata['address'], metadata['file_data']
        url = os.path.join(address, cmd)
        response, code = post_storage(url, data)
        if response_failed(code):
            return fetch_error_msg(code)
        else:
            data = {
                'node_data': {
                    'address': address
                },
                'file_metadata': {
                    'file_data': data
                },
                'file': response
            }
            return func(args[0], data)
    return wrapper


def post_storage(url, data):
    try:
        x = requests.post(url, json=data)
        try:
            return x.content, x.status_code
        except ValueError:
            return None, CODE_CORRUPTED_RESPONSE
    except requests.exceptions.ConnectionError:
        return None, CODE_CONNECTION_ERROR


def post(uri, data, model):
    try:
        url = os.path.join(NAME_NODE_ADDRESS, uri)
        x = requests.post(url, json=data)
        try:
            x_data = model.parse_raw(x.content)
            return x_data, x.status_code
        except ValidationError:
            return None, CODE_CORRUPTED_RESPONSE
    except requests.exceptions.ConnectionError:
        return None, CODE_CONNECTION_ERROR


def response_failed(status_code):
    return error_dict.get(status_code) is not None


def fetch_error_msg(status_code):
    return error_dict[status_code]


class Client:

    def __init__(self, cwd):
        self.cwd = cwd

    def set_cwd(self, new_cwd):
        self.cwd = new_cwd

    def get_cwd(self):
        return self.cwd

    @name_error_handler
    def dfs_init(self, data):
        """
        Initialize the client storage on a new system,
        remove any existing file in the dfs root
        directory and return available size.

        :returns size of available storage, set cwd to '/'
        """
        response = data['response']
        size = response['size']
        return f'Available size: {size} bytes' \
               f' or {size / 1024} kilobytes or' \
               f' {size / 1024 / 1024} megabytes or' \
               f' {size / 1024 / 1024 / 1024} gigabytes.'

    @name_error_handler
    def dfs_file_create(self, data):
        """
        Allows to create a new empty file.
        """
        response = data['response']
        console_data = data['console_data']
        filename = console_data['filename']
        node_ip = response['node_ip']
        return f'The new file with name \'{filename}\' was created at \'{node_ip}\'.'

    @storage_error_handler
    def dfs_file_download(self, data):
        file = data['file']
        node_address = data['node_data']['address']
        filename = data['file_metadata']['path']
        with open(os.path.basename(filename), 'w') as out:
            out.write(file)
        return f'File {filename} has been successfully downloaded from node at {node_address}!'

    @storage_error_handler
    def dfs_file_upload(self, data):
        node_address = data['node_data']['address']
        filename = data['file_metadata']['path']
        return f'File {filename} has been successfully uploaded to node at {node_address}'

    @name_error_handler
    def dfs_file_read(self, data):
        """
        Allows to read any file from DFS (download a file from the DFS to the Client side).
        """
        console_data = data['console_data']
        response = data['response']
        metadata = {
            'cmd': 'send',
            'file_data': {
                'path': console_data['filename']
            },
            'address': response['node_ip']
        }
        return self.dfs_file_download(metadata)

    @name_error_handler
    def dfs_file_write(self, data):
        """
        Allows to put any file to DFS (upload a file from the Client side to the DFS)
        """
        console_data = data['console_data']
        response = data['response']
        metadata = {
            'cmd': 'rcv',
            'file_data': {
                'path': console_data['filename']
            },
            'address': response['node_ip']
        }
        return self.dfs_file_upload(metadata)

    @name_error_handler
    def dfs_file_delete(self, data):
        """
        Should allow to delete any file from DFS
        """
        console_data = data['console_data']
        response = data['response']
        filename = console_data['filename']
        return f'File {filename} has been successfully deleted from node {response["node_ip"]}!'

    def dfs_file_info(self, data):
        """
        Should provide information about the file (any useful information - size, node id, etc.)
        """

    def dfs_file_copy(self, data):
        """
        Should allow to create a copy of file.
        """

    def dfs_file_move(self, data):
        """
        Should allow to move a file to the specified path.
        """

    def dfs_dir_open(self, data):
        """
        Should allow to change directory
        """

    def dfs_dir_read(self, data):
        """
        Should return list of files, which are stored in the directory.
        """

    def dfs_dir_make(self, data):
        """
        Should allow to create a new directory.
        """

    def dfs_dir_delete(self, data):
        """
        Should allow to delete directory.  If the directory contains
        files the system should ask for confirmation from the
        user before deletion.
        """
