from flask import Flask, request
from . import database as db
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

def send_init():
    pass

def check_request_data(data):
    if data is None:
        raise BadRequest()

@app.route('/dfs_init', methods=['GET'])
def init():
    send_init()
    size = db.get_available_size()
    return {'size': size}

@app.route('/new_node', methods=['POST'])
def add_new_node():
    data = request.get_json()
    check_request_data(data)
    new_id = db.add_node(request.remote_addr(), data['size'])
    return {'id': new_id}, 200

@app.route('/dfs_file_create', methods=['POST'])
def file_create():
    data = request.get_json()
    check_request_data(data)
    db.create_file(data['filename'])
    return {}, 200

@app.route('/dfs_file_read', methods=['POST'])
def file_read():
    """
    TODO: add checking
    """
    data = request.get_json()
    check_request_data(data)
    node = db.find_node_by_file(data['filename'])
    return {'ip': node.addr}, 200

@app.route('/dfs_file_write', methods=['POST'])
def file_write():
    data = request.get_json()
    check_request_data(data)
    size = data['size']
    filename = data['filename']
    ip = db.write_file(filename, size)
    return {'ip': ip}, 200

@app.route('/dfs_file_delete', methods=['POST'])
def file_delete():
    data = request.get_json()
    check_request_data(data)
    filename = data['filename']
    ip = db.delete_file(filename)
    return {}, 200

@app.route('/dfs_file_info', methods=['POST'])
def file_info():
    data = request.get_json()
    check_request_data(data)
    filename = data['filename']
    file_info = db.get_file_info(filename)
    return file_info, 200

@app.route('/dfs_file_copy', methods=['POST'])
def file_copy():
    data = request.get_json()
    check_request_data(data)
    filename = data['filename']
    new_filename = data['cp_filename']
    db.copy_file(filename, new_filename)
    return {}, 200

@app.route('/dfs_file_move', methods=['POST'])
def file_move():
    data = request.get_json()
    check_request_data(data)
    filename = data['filename']
    new_filename = data['mv_filename']
    db.move_file(filename, new_filename)
    return {}, 200

@app.route('/dfs_read_directory', methods=['POST'])
def read_directory():
    data = request.get_json()
    check_request_data(data)
    dirname = data['dirname']
    info = db.dir_read(dirname)
    return info, 200

@app.route('/dfs_make_directory', methods=['POST'])
def make_directory():
    data = request.get_json()
    check_request_data(data)
    dirname = data['dirname']
    db.dir_make(dirname)
    return {}, 200

@app.route('/dfs_delete_directory', methods=['POST'])
def delete_directory():
    data = request.get_json()
    check_request_data(data)
    dirname = data['dirname']
    db.dir_delete(dirname)
    return {}, 200
