from namenode.database import *


def query_storage(node_id, path) -> List[str]:
    subq = PendingFileNode.q().filter(PendingFileNode.storage_id != node_id, PendingFileNode.path == path).subquery()
    return [node.storage_ip for node in session.query(Node.storage_ip).join(subq, Node.storage_id == subq.c.storage_id)]


def query_file(path: str) -> bool:
    return File.exists(path)
