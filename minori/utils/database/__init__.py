from .db import Database, DatabaseHook
from .mongo import Collection

db = Database()

__all__ = ["db", "DatabaseHook", "Collection"]
