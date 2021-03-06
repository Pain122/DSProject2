import click
import posixpath
import os
from client.client import client

def get_cwd():
    with open('cwd.txt', 'r') as cwd:
        return cwd.readline()


def format_filename(filename):
    filename = click.format_filename(filename)
    path = posixpath.join(get_cwd(), filename)
    return path


@click.group()
@click.pass_context
def dfs(ctx):
    """ Root command for distributed file system CLI """
    pass

@dfs.command(name='init')
def dfs_init():
    """
    Initialize the client storage on a new system,
    should remove any existing file in the dfs root
    directory and return available size.
    """
    with open('cwd.txt', 'w') as cwd:
        cwd.write('/')
    data = {}
    metadata = {
        'cmd': 'dfs_init',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_init(metadata)
    click.echo(msg)


@dfs.group(name='file')
@click.pass_context
def dfs_file(ctx):
    pass

@dfs_file.command(name='create')
@click.argument('filename', type=click.Path())
def dfs_file_create(filename):
    """
    Should allow to create a new empty file.
    """
    
    path = format_filename(filename)
    data = {'path': path}
    metadata = {
        'cmd': 'dfs_file_create',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_file_create(metadata)
    click.echo(msg)


@dfs_file.command(name='read')
@click.argument('filename', type=click.Path())
def dfs_file_read(filename):
    """
    Should allow to read any file from DFS (download a file from the DFS to the Client side).
    """
    
    path = format_filename(filename)
    data = {'path': path}
    metadata = {
        'cmd': 'dfs_file_read',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_file_read(metadata)
    click.echo(msg)


@dfs_file.command(name='write')
@click.argument('filename', type=click.Path(exists=True))
def dfs_file_write(filename):
    """
    Should allow to put any file to DFS (upload a file from the Client side to the DFS)
    """
    
    file = click.format_filename(filename)
    size = os.path.getsize(file)
    path = format_filename(filename)
    with open(file, 'rb') as f:
        data = {
            'path': path,
            'size': size
        }
        console_data = {
            'path': path,
            'file': f
        }
        metadata = {
            'cmd': 'dfs_file_write',
            'payload': data,
            'console_data': console_data
        }
        # mp_encoder = MultipartEncoder(
        #     fields={
        #         'path': console_data['path'],
        #         'file': (console_data['path'], console_data['file'], 'text/plain'),
        #     }
        # )
        # response = requests.post("http://10.242.1.154:8000/create",
        #               data=mp_encoder,
        #               headers={'Content-Type': mp_encoder.content_type})
        # click.echo(response)
        msg = client.dfs_file_write(metadata)
        click.echo(msg)


@dfs_file.command(name='delete')
@click.argument('filename', type=click.Path())
def dfs_file_delete(filename):
    """
    Should allow to delete any file from DFS
    """
    
    path = format_filename(filename)
    data = {'path': path}
    metadata = {
        'cmd': 'dfs_file_delete',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_file_delete(metadata)
    click.echo(msg)


@dfs_file.command(name='info')
@click.argument('filename', type=click.Path())
def dfs_file_info(filename):
    """
    Should provide information about the file (any useful information - size, node id, etc.)
    """
    
    path = format_filename(filename)
    data = {'path': path}
    metadata = {
        'cmd': 'dfs_file_info',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_file_info(metadata)
    click.echo(msg)


@dfs_file.command(name='copy')
@click.argument('filename', type=click.Path())
@click.argument('dest', type=click.Path())
def dfs_file_copy(filename, dest):
    """
    Should allow to create a copy of file.
    """
    
    path = format_filename(filename)
    dest = format_filename(dest)
    data = {
        'path': path,
        'new_path': dest
    }
    metadata = {
        'cmd': 'dfs_file_copy',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_file_copy(metadata)
    click.echo(msg)


@dfs_file.command(name='move')
@click.argument('filename', type=click.Path())
@click.argument('dest', type=click.Path())
def dfs_file_move(filename, dest):
    """
    Should allow to move a file to the specified path.
    """
    
    path = format_filename(filename)
    dest = format_filename(dest)
    data = {
        'path': path,
        'new_path': dest
    }
    metadata = {
        'cmd': 'dfs_file_move',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_file_move(metadata)
    click.echo(msg)


@dfs.group(name='dir')
@click.pass_context
def dfs_dir(ctx):
    pass

@dfs_dir.command(name='open')
@click.argument('name', type=click.Path())
def dfs_dir_open(name):
    """
    Should allow to change directory
    """
    import re
    path = format_filename(name)
    data = {
        'path': client.get_cwd()
    }
    console_data = {
        'dir': path
    }
    metadata = {
        'cmd': 'dfs_read_directory',
        'payload': data,
        'console_data': console_data
    }
    msg = client.dfs_dir_open(metadata)
    if re.fullmatch(r"You are now in /[a-zA-Z/]*\.", msg):
        with open('cwd.txt', 'w') as cwd:
            cwd.write(re.search(r'(/.*)\.', msg).group(1))
    click.echo(msg)


@dfs_dir.command(name='read')
@click.argument('name', type=click.Path())
def dfs_dir_read(name):
    """
    Should return list of files, which are stored in the directory.
    """
    
    path = format_filename(name)
    data = {
        'path': path
    }
    metadata = {
        'cmd': 'dfs_read_directory',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_dir_read(metadata)
    click.echo(msg)


@dfs_dir.command(name='make')
@click.argument('name', type=click.Path())
def dfs_dir_make(name):
    """
    Should allow to create a new directory.
    """
    
    path = format_filename(name)
    data = {
        'path': path
    }
    metadata = {
        'cmd': 'dfs_make_directory',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_dir_make(metadata)
    click.echo(msg)


@dfs_dir.command(name='delete')
@click.argument('name', type=click.Path())
def dfs_dir_delete(name):
    # TODO: verify first with name node, then ask user to confirm

    """
    Should allow to delete directory.  If the directory contains
    files the system should ask for confirmation from the
    user before deletion.
    """
    
    path = format_filename(name)
    data = {
        'path': path
    }
    metadata = {
        'cmd': 'dfs_delete_directory',
        'payload': data,
        'console_data': data
    }
    msg = client.dfs_dir_delete(metadata)
    click.echo(msg)


@dfs_dir.command(name='cwd')
def cwd():
    click.echo(get_cwd())


if __name__ == '__main__':
    print(os.getenv("NAMENODE_ADDR"))
