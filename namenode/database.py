from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, ForeignKeyConstraint, alias, BigInteger
from sqlalchemy.sql.expression import insert
from sqlalchemy.orm import relationship, Query
from config import *
from typing import List
from sqlalchemy.sql.selectable import Exists
from utils.serialize.general import StorageListModel
import logging
import string


def db_init() -> None:
    File.q().delete(synchronize_session='fetch')
    FallenFileNode.q().delete(synchronize_session='fetch')
    Directory.q().delete(synchronize_session='fetch')
    session.commit()
    Directory.create('/')


def get_dir_model(path: str) -> DirectoryModel:
    files = [SimpleFileModel.from_orm(file) for file in File.query_by_dir(path)]
    dirs = [SimpleFileModel.from_orm(dir) for dir in Directory.query_by_dir(path)]
    files += dirs
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
    def query_by_node_ids(cls, node_ids: List[str] or str) -> Query:
        if isinstance(node_ids, str):
            node_ids = [node_ids]
        q = session.query(cls).filter(cls.storage_id.in_(node_ids))
        return q

    @classmethod
    def query_by_dir(cls, path: str, q: Query = None) -> Query:
        if q is None:
            q = cls.q()
        format_path = path.replace('/', '\\/')
        if format_path[-3:] != '\\/':
            format_path += '\\/'
        return q.filter(cls.path.op('~')(f'({path}[A-z]+)'))


class PendingFileNode(Base):
    __tablename__ = 'pending_file_node'
    path = Column(String, ForeignKey('files.path', ondelete="CASCADE"), primary_key=True)
    storage_id = Column(String, ForeignKey('nodes.storage_id', ondelete="CASCADE"), primary_key=True)

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)

    @classmethod
    def add_task(cls, file: File, nodes: List[Node] or Node) -> None:
        if isinstance(nodes, Node):
            nodes.available_size -= file.size
            session.add(cls(path=file.path, storage_id=nodes.id))
            session.commit()
            return
        else:
            for node in nodes:
                node.available_size -= file.size
            objects = [cls(path=file.path, storage_id=node.storage_id) for node in nodes]
            session.add_all(objects)
            session.commit()

    @classmethod
    def add_tasks(cls, mapping: dict):
        objects = []
        logger.info(mapping)
        if mapping is None:
            return
        for storage_id, paths in mapping.items():
            for path in paths:
                print(path, storage_id)
                objects.append(cls(path=path, storage_id=storage_id))
        session.add_all(objects)
        session.commit()

    @classmethod
    def complete_task(cls, path: str, node_id: str) -> None:
        cls.q().filter(cls.path == path, cls.storage_id == node_id).delete(synchronize_session='fetch')
        File.append_storages(path, node_id)

    @classmethod
    def fail_task(cls, path: str, node_id: str) -> None:
        cls.q().filter(cls.path == path, cls.storage_id == node_id).delete(synchronize_session='fetch')
        size = File.query_by_paths(path, session.query(File.size)).scalar()[0]
        node = Node.query_by_ids(node_id).scalar()
        node.available_size += size
        session.commit()


class FallenFileNode(Base):
    __tablename__ = 'fallen_file_node'
    path = Column(String, primary_key=True)
    storage_id = Column(String, ForeignKey('nodes.storage_id', ondelete="CASCADE"), primary_key=True)

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)


class File(Base):
    __tablename__ = 'files'
    path = Column(String, primary_key=True)
    size = Column(Integer)
    storages = relationship("Node", secondary='file_node', cascade='all, delete', passive_deletes=True)
    # const = ForeignKeyConstraint(['path'], ['file_node.path'], ondelete='DELETE')

    @classmethod
    def q(cls) -> Query:
        return session.query(cls)

    @classmethod
    def create(cls, **new_file) -> File:
        new_obj = cls(**new_file)
        session.add(new_obj)
        session.commit()
        return new_obj

    @classmethod
    def _get_storages_from_model(cls, storages: List[StorageModel]) -> List[Node]:
        return Node.query_by_ids([storage.storage_id for storage in storages]).all()

    @classmethod
    def create_many(cls, new_files: List[dict]) -> List['File']:
        new_objs = [cls(**new_file) for new_file in new_files]
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
        return num_of_deleted

    @classmethod
    def query_by_dir(cls, path: str, q: Query = None) -> Query:
        if q is None:
            q = cls.q()
        format_path = path.replace('/', '\\/')
        if format_path[-3:] != '\\/':
            format_path += '\\/'
        return q.filter(cls.path.op('~')(f'({path}[A-z]+)'))

    @classmethod
    def append_storages(cls, path: str, storage_ids: List[str] or str) -> None:
        if isinstance(storage_ids, str):
            storage_ids = [storage_ids]
        file = cls.query_by_paths(path).scalar()
        nodes = Node.query_by_ids(storage_ids).all()
        file.storages += nodes
        session.commit()


class Node(Base):
    __tablename__ = 'nodes'
    storage_id = Column(String, primary_key=True)
    storage_ip = Column(String)
    available_size = Column(BigInteger)
    active = Column(Boolean, default=True)

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
    def query_by_ids(cls, node_ids: List[str] or str = None) -> Query:
        if isinstance(node_ids, str):
            node_ids = [node_ids]
        q = cls.q()
        if node_ids is None:
            return q
        return q.filter(cls.storage_id.in_(node_ids))

    @classmethod
    def delete(cls, ids: List[int] or int) -> int:
        q = cls.query_by_ids(ids)
        num_of_deleted = q.delete(synchronize_session='fetch')
        session.commit()
        return num_of_deleted

    @classmethod
    def get_node_models(cls, node_ids: List[int] or int = None) -> StorageListModel:
        node_objs = cls.query_by_ids(node_ids=node_ids).filter(cls.active == True).all()
        storages = [StorageModel.from_orm(node_obj) for node_obj in node_objs]
        return StorageListModel(storages=storages)

    @classmethod
    def query_by_dir(cls, path: str) -> Query:
        subq = FileNode.query_by_dir(path).subquery()
        return cls.q().join(subq, Node.storage_id == subq.c.storage_id).filter(Node.active == True)

    @classmethod
    def get_sorted_nodes(cls, size=0) -> List['Node']:
        return cls.q().filter(cls.available_size > size, Node.active==True).order_by(Node.available_size.desc()).all() or []

    def fall(self) -> dict or None:
        if not self.active:
            return None
        self.active = False
        q_pfilenode = PendingFileNode.q().filter(PendingFileNode.storage_id == self.storage_id)
        q_pfilenode_s = q_pfilenode.subquery()
        q_files = session.query(File).join(q_pfilenode_s, File.path == q_pfilenode_s.c.path)
        q_filenode = FileNode.query_by_node_ids(self.storage_id)
        ins = insert(FallenFileNode).from_select(['path', 'storage_id'], q_filenode)
        session.execute(ins)
        q_filenode.delete(synchronize_session='fetch')
        q_pfilenode.delete(synchronize_session='fetch')
        session.commit()
        distr_mapping, send_mapping = self.distribute_files(q_files.order_by(File.size.desc()))
        PendingFileNode.add_tasks(distr_mapping)
        return send_mapping

    def up(self) -> List[str] or None:
        if self.active:
            return
        self.active = True
        q_ffilenode = FallenFileNode.q().filter(FallenFileNode.storage_id == self.storage_id)
        subq = File.q().subquery()
        ins = insert(FileNode).from_select(['path', 'storage_id'], q_ffilenode.join(subq, FallenFileNode.path == subq.c.path))
        session.execute(ins)
        delete_paths = [path[0] for path in q_ffilenode.except_all(q_ffilenode.join(subq, FallenFileNode.path == subq.c.path)).from_self(FallenFileNode.path)]
        q_ffilenode.delete(synchronize_session='fetch')
        session.commit()
        return delete_paths

    def distribute_files(self, qfile: Query) -> (dict, dict):
        def key(obj):
            return obj.available_size
        nodes = self.get_sorted_nodes()
        files = qfile.all()
        res_dict = {node.storage_id: [] for node in nodes}
        send_dict = {node: [] for node in nodes}
        for file in files:
            path, size = file.path, file.size
            send_node = None
            recv_node = None
            flag = True
            for node in nodes:
                if node in file.storages:
                    send_node = node
                    continue
                if node.available_size > size and flag:
                    recv_node = node
                    flag = False
            nodes.sort(key=key, reverse=True)
            if send_node is None or recv_node is None:
                continue
            recv_node.available_size -= size
            res_dict[recv_node.storage_id].append(path)
            file_model = FileModel.from_orm(file)
            file_model.storages = [StorageModel.from_orm(recv_node)]
            send_dict[send_node].append(file_model)
        return res_dict, send_dict


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
        return cls.q().filter(cls.path == path).count() != 0

    @classmethod
    def query_by_dir(cls, path: str, q: Query = None) -> Query:
        if q is None:
            q = cls.q()
        format_path = path.replace('/', '\\/')
        if format_path[-3:] != '\\/':
            format_path += '\\/'
        return q.filter(cls.path.op('~')(f'({path}[A-z]+)'))

    @classmethod
    def delete(cls, path: str) -> None:
        cls.q().filter(Directory.path == path).delete(synchronize_session='fetch')
        session.commit()
