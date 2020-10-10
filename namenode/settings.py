import sqlalchemy as sql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.serialize.general import *

db_engine = create_engine('sqlite:///test.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=db_engine)
session = Session()
# DEBUG = True
# DEBUG_CONFIG = {
#     'inodes': True,
#     'inodes_config': {
#         [
#             StorageModel(storage_id=1, storage_ip='0.0.0.0', available_storage=5e9).dict(),
#             StorageModel(storage_id=2, storage_ip='0.0.0.0', available_storage=5e9).dict(),
#             StorageModel(storage_id=3, storage_ip='0.0.0.0', available_storage=5e9).dict(),
#             StorageModel(storage_id=4, storage_ip='0.0.0.0', available_storage=5e9).dict()
#         ]
#     }
# }