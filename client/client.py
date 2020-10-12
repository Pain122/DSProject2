import requests
import posixpath
from pydantic.error_wrappers import ValidationError
from requests_toolbelt.multipart.encoder import MultipartEncoder
from utils.serialize.general import *
from utils.serialize.namenode import *
from config import *
cmd_model_map = {
    'dfs_init': InitResponse,
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
        cmd, payload, console_data = metadata['cmd'], metadata['payload'], metadata['console_data']
        model = cmd_model_map[cmd]
        response, code = post(cmd, payload, model)
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
        url = posixpath.join(f'http://{address}', cmd)
        response, code = post_storage(url, data=data, headers={'Content-Type': data.content_type})
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


def post_storage(url, data, headers):
    try:
        x = requests.post(url, data=data, headers=headers)
        try:
            return x.content, x.status_code
        except ValueError:
            return None, CODE_CORRUPTED_RESPONSE
    except requests.exceptions.ConnectionError:
        return None, CODE_CONNECTION_ERROR


def post(uri, data, model):
    try:
        url = posixpath.join(NAME_NODE_ADDRESS, uri)
        x = requests.post(url, json=data)
        if not x.status_code.ok:
            return None, x.status_code
        try:
            x_data = model.parse_raw(x.content).dict()
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
               f' or {size // 1024} kilobytes or' \
               f' {size // 1024 // 1024} megabytes or' \
               f' {size // 1024 // 1024 // 1024} gigabytes.'

    @name_error_handler
    def dfs_file_create(self, data):
        """
        Allows to create a new empty file.
        """
        console_data, response = data['console_data'], data['response']
        filename = response['path']
        storages = '\n'.join([storage['storage_ip'] for storage in response['storages']])
        return f'The new file with name \'{filename}\' was created at:\n{storages}.'

    @storage_error_handler
    def dfs_file_download(self, data):
        file = data['file']
        node_address = data['node_data']['address']
        filename = data['file_metadata']['file_data'].fields['path']
        with open(posixpath.basename(filename), 'wb') as out:
            out.write(file)
        return f'File \'{filename}\' has been successfully downloaded from node at {node_address}!'

    @storage_error_handler
    def dfs_file_upload(self, data):
        node_address = data['node_data']['address']
        return f'File has been successfully uploaded to node at {node_address}'

    @name_error_handler
    def dfs_file_read(self, data):
        """
        Allows to read any file from DFS (download a file from the DFS to the Client side).
        """
        console_data, response = data['console_data'], data['response']
        storages = [storage['storage_ip'] for storage in response['storages']]
        metadata = {
            'cmd': 'send',
            'file_data': MultipartEncoder(
                fields={
                    'path': response['path']
                }
            ),
            'address': storages[0]
        }
        return self.dfs_file_download(metadata)

    @name_error_handler
    def dfs_file_write(self, data):
        """
        Allows to put any file to DFS (upload a file from the Client side to the DFS)
        """
        console_data, response = data['console_data'], data['response']
        storages = [storage['storage_ip'] for storage in response['storages']]
        mp_encoder = MultipartEncoder(
            fields={
                'path': console_data['path'],
                'file': (console_data['path'], console_data['file'], 'text/plain'),
            }
        )
        metadata = {
            'cmd': 'create',
            'file_data': mp_encoder,
            'address': storages[0]
        }
        return self.dfs_file_upload(metadata)

    @name_error_handler
    def dfs_file_delete(self, data):
        """
        Should allow to delete any file from DFS
        """
        console_data, response = data['console_data'], data['response']
        storages = '\n\t'.join([storage['storage_ip'] for storage in response['storages']])
        filename = response['path']
        return f'File {filename} has been successfully deleted from nodes:' \
               f'\n{storages}!\n' \
               f'Reclaimed storage: {response["size"]}'

    @name_error_handler
    def dfs_file_info(self, data):
        """
        Should provide information about the file (any useful information - size, node id, etc.)
        """
        console_data, response = data['console_data'], data['response']
        storages = '\n\t'.join([storage['storage_ip'] for storage in response['storages']])
        filename = response['path']
        return f'Full path in VFS: {filename}\n' \
               f'File is replicated at nodes:\n{storages}!\n' \
               f'Each replica occupies: {response["size"]}'

    @name_error_handler
    def dfs_file_copy(self, data):
        """
        Should allow to create a copy of file.
        """
        console_data, response = data['console_data'], data['response']
        storages = '\n\t'.join([storage['storage_ip'] for storage in response['storages']])
        filename = response['path']
        return f'File \'{filename}\' at nodes:' \
               f'\n{storages}!\n' \
               f'has been copied to: {response["path"]}'

    @name_error_handler
    def dfs_file_move(self, data):
        """
        Should allow to move a file to the specified path.
        """
        console_data, response = data['console_data'], data['response']
        storages = '\n\t'.join([storage['storage_ip'] for storage in response['storages']])
        filename = response['path']
        return f'File \'{filename}\' at nodes:' \
               f'\n{storages}!\n' \
               f'has been moved to: {response["path"]}'

    @name_error_handler
    def dfs_dir_open(self, data):
        """
        Should allow to change directory
        """
        console_data, response = data['console_data'], data['response']
        filenames = [file['path'] for file in response['files']]
        directory = console_data['dir']
        if directory in filenames:
            self.cwd = posixpath.join(self.cwd, directory)
            return f'You are now in {self.cwd}.'
        else:
            return f'Directory \'{directory}\' doesn\'t exist!'

    @name_error_handler
    def dfs_dir_read(self, data):
        """
        Should return list of files, which are stored in the directory.
        """
        console_data, response = data['console_data'], data['response']
        filenames = [posixpath.basename(file['path']) for file in response['files']]
        filename = response['path']
        filenames_string = '\n\t'.join(filenames)
        return f'Directory \'{filename}\' contains the following files:\n' \
               f'{filenames_string}'

    @name_error_handler
    def dfs_dir_make(self, data):
        """
        Should allow to create a new directory.
        """
        console_data, response = data['console_data'], data['response']
        storages = '\n\t'.join([storage['storage_ip'] for storage in response['storages']])
        filename = response['path']
        return f'The directory \'{filename}\' at nodes:' \
               f'\n{storages}!\n' \
               f'has been successfully created!'

    @name_error_handler
    def dfs_dir_delete(self, data):
        """
        Should allow to delete directory.  If the directory contains
        files the system should ask for confirmation from the
        user before deletion.
        """
        console_data, response = data['console_data'], data['response']
        storages = '\n\t'.join([storage['storage_ip'] for storage in response['storages']])
        filename = response['path']
        return f'The directory \'{filename}\' at nodes:' \
               f'\n{storages}!\n' \
               f'has been successfully removed!'
