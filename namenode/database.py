from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from .settings import Base
from sqlalchemy.orm import relationship, backref, Query
from .settings import *
from typing import List
from sqlalchemy.sql.selectable import Exists
from utils.serialize.general import StorageListModel


def db_init() -> None:
    File.q().delete(synchronize_session='fetch')
    FileNode.q().delete(synchronize_session='fetch')
    session.commit()


def get_dir_model(path: str) -> DirectoryModel:
    files = [FileModel.from_orm(file) for file in File.query_by_dir(path)]
    storages = [StorageModel.from_orm(storage) for storage in Node.query_by_dir(path)]
    return DirectoryModel(files=files, storages=storages, path=path)


class FileNode(Base):
    __tablename__ = 'file_node'
    path = Column(String, ForeignKey('files.path', ondelete="CASCADE"), primary_key=True)
    storage_id = Column(String, ForeignKey('nodes.storage_id', ondelete="CASCADE"), primary_key=True)

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)

    @classmethod
    def query_by_paths(cls, paths: List[str] or str) -> Query:
        if isinstance(paths, str):
            paths = [paths]
        q = session.query(cls).filter(cls.path.in_(paths))
        return q

    @classmethod
    def query_by_node_ids(cls, node_ids: List[int] or int) -> Query:
        if isinstance(node_ids, int):
            node_ids = [node_ids]
        q = session.query(cls).filter(cls.storage_id.in_(node_ids))
        return q


class File(Base):
    __tablename__ = 'files'
    path = Column(String, primary_key=True)
    size = Column(Integer)
    storages = relationship("Node", secondary='file_node', cascade='all, delete')

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)

    @classmethod
    def create(cls, new_file: FileModel) -> File:
        dict_obj = cls._construct_semimodels([new_file])
        new_obj = cls(**dict_obj)
        session.add(new_obj)
        session.commit()
        return new_obj

    @classmethod
    def _get_storages_from_model(cls, storages: List[StorageModel]) -> List[Node]:
        return Node.query_by_ids([storage.storage_id for storage in storages]).all()

    @classmethod
    def _construct_semimodels(cls, files: List[FileModel]) -> List[dict] or dict:
        if len(files) == 1:
            temp_dict = files[0].dict()
            temp_dict['storages'] = cls._get_storages_from_model(files[0].storages)
            return temp_dict
        res = []
        for file in files:
            temp_dict = file.dict()
            temp_dict['storages'] = cls._get_storages_from_model(file.storages)
            res.append(temp_dict)
        return res

    @classmethod
    def create_many(cls, new_files: List[FileModel]) -> List['File']:
        dict_objs = cls._construct_semimodels(new_files)
        new_objs = [cls(**dict_obj) for dict_obj in dict_objs]
        session.add_all(new_objs)
        session.commit()
        return new_objs

    @classmethod
    def query_by_paths(cls, paths: List[str] or str = None, q: Query = None) -> Query:
        q = cls.q() if q is None else q
        if paths is None:
            return q
        if isinstance(paths, str):
            paths = [paths]
        q = q.filter(cls.path.in_(paths))
        return q

    @classmethod
    def exists(cls, paths: List[str] or str, q: Query = None) -> bool:
        return cls.query_by_paths(paths, q=q).count() > 0

    @classmethod
    def query_real_files(cls, q: Query = None) -> Query:
        if q is None:
            q = cls.q()
        q = q.join(FileNode)
        return q

    @classmethod
    def delete(cls, paths: List[str] or str) -> int:
        q = cls.query_by_paths(paths, cls.q())
        num_of_deleted = q.delete(synchronize_session='fetch')
        FileNode.query_by_paths(paths).delete(synchronize_session='fetch')
        return num_of_deleted

    @classmethod
    def query_by_dir(cls, path: str, q: Query = None) -> Query:
        if q is None:
            q = cls.q()
        return q.filter(File.path.startswith(path))


class Node(Base):
    __tablename__ = 'nodes'
    storage_id = Column(String, primary_key=True)
    storage_ip = Column(String)
    available_size = Column(Integer)
    # files = relationship("File", secondary='file_node', cascade="all, delete-orphan", single_parent=True)

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)

    @classmethod
    def create(cls, new_node: StorageModel) -> 'Node':
        new_obj = cls(**new_node.dict())
        session.add(new_obj)
        session.commit()
        return new_obj

    @classmethod
    def create_many(cls, new_nodes: List[StorageModel]) -> List['Node']:
        new_objs = [cls(**new_node.dict()) for new_node in new_nodes]
        session.add_all(new_objs)
        session.commit()
        return new_objs

    @classmethod
    def query_by_ids(cls, node_ids: List[int] or int = None) -> Query:
        if isinstance(node_ids, int):
            node_ids = [node_ids]
        q = cls.q()
        if node_ids is None:
            return q
        return q.filter(cls.storage_id.in_(node_ids))

    @classmethod
    def delete(cls, ids: List[int] or int) -> int:
        q = cls.query_by_ids(ids)
        q_a = FileNode.query_by_node_ids(ids)
        num_of_deleted = q.delete(synchronize_session='fetch')
        q_a.delete(synchronize_session='fetch')
        session.commit()
        return num_of_deleted

    @classmethod
    def get_node_models(cls, node_ids: List[int] or int = None) -> StorageListModel:
        node_objs = cls.query_by_ids(node_ids=node_ids).all()
        storages = [StorageModel.from_orm(node_obj) for node_obj in node_objs]
        return StorageListModel(storages=storages)

    @classmethod
    def query_by_dir(cls, path: str) -> Query:
        return cls.q().join(FileNode).filter(FileNode.path.startswith(path))

class Directory(Base):
    __tablename__ = 'dirs'
    path = Column(String, primary_key=True)

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)

    @classmethod
    def create(cls, path: str) -> 'Directory':
        existing_dir = cls._exist(path)
        if existing_dir is not None:
            return existing_dir
        obj = cls(path=path)
        session.add(obj)
        session.commit()
        return obj


    @classmethod
    def _exist(cls, path: str) -> 'Directory':
        q = cls.q()
        return q.filter(cls.path == path).scalar()

    @classmethod
    def exist(cls, path: str) -> bool:
        return cls._exist(path) is not None

    @classmethod
    def delete(cls, path: str) -> None:
        cls.q().filter(Directory.path == path).delete(synchronize_session='fetch')
        session.commit()
