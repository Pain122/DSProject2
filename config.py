import os

import sqlalchemy as sql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.serialize.general import *

"""
General config
"""
NAME_NODE_ADDRESS = "http://228.228.228.228:80"
DEBUG = True
WORKING_DIR = 'C:\\Users\\pavel\\Innopolis\\DS\\Project2\\working_dir_example'

# ERROR CODES
CODE_CONNECTION_ERROR = 418
CODE_VALIDATION_ERROR = 422
CODE_CORRUPTED_RESPONSE = 500
CODE_NO_NODE_AVAILABLE = 501
CODE_NOT_ENOUGH_STORAGE = 502
CODE_NODE_DISCONNECTED = 503
CODE_FILE_NOT_FOUND = 504
CODE_NO_SUCH_DIRECTORY = 505
CODE_INTEGRITY_ERROR = 506
CODE_NOT_EMPTY_DIRECTORY = 507


"""
Namenode config
"""
db_engine = create_engine('sqlite:///test.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=db_engine)
session = Session()

"""
Client config
"""
CONNECTION_ERROR = 'Connection with server is lost!'
VALIDATION_ERROR = 'Some of the data you sent were invalid!'
CORRUPTED_RESPONSE = 'The response from server is corrupted!'
NO_NODE_AVAILABLE = 'No nodes are available to store this file!'
NOT_ENOUGH_STORAGE = 'There is not enough memory to store your file!'
NODE_DISCONNECTED = 'Node storing the file disconnected!'
FILE_NOT_FOUND = 'File with such name was not found!'
NO_SUCH_DIRECTORY = 'Directory with such name doesn\'t exist!'
INTEGRITY_ERROR = 'One of the storage servers reported an integrity error!'
NOT_EMPTY_DIRECTORY = 'Directory is not empty!'

error_dict = {
    CODE_CORRUPTED_RESPONSE: CORRUPTED_RESPONSE,
    CODE_VALIDATION_ERROR: VALIDATION_ERROR,
    CODE_CONNECTION_ERROR: CONNECTION_ERROR,
    CODE_NO_NODE_AVAILABLE: NO_NODE_AVAILABLE,
    CODE_NOT_ENOUGH_STORAGE: NOT_ENOUGH_STORAGE,
    CODE_NODE_DISCONNECTED: NODE_DISCONNECTED,
    CODE_FILE_NOT_FOUND: FILE_NOT_FOUND,
    CODE_NO_SUCH_DIRECTORY: NO_SUCH_DIRECTORY,
    CODE_INTEGRITY_ERROR: INTEGRITY_ERROR,
    CODE_NOT_EMPTY_DIRECTORY: NOT_EMPTY_DIRECTORY
}