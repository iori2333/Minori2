from abc import ABC, abstractmethod
from typing import Optional, Sequence, Type, TypeVar
from bson import ObjectId
from pymongo.database import Database as MongoDatabase

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent

from .mongo import db, Collection

TM = TypeVar("TM", bound="DatabaseHook")


class DatabaseHook(ABC):

    def __init__(self, db: MongoDatabase) -> None:
        self.db = db

    @abstractmethod
    def on_group_message(
        self,
        event: GroupMessageEvent,
        inserted: ObjectId,
        collection: Collection[GroupMessageEvent],
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def on_private_message(
        self,
        event: PrivateMessageEvent,
        inserted: ObjectId,
        collection: Collection[PrivateMessageEvent],
    ) -> None:
        raise NotImplementedError()


class Database:

    def __init__(self):
        self.db = db
        self._group = Collection("group", GroupMessageEvent)
        self._private = Collection("private", PrivateMessageEvent)
        self._hooks: list[DatabaseHook] = []

    def insert(self, event: MessageEvent) -> None:
        object_id: ObjectId
        if isinstance(event, GroupMessageEvent):
            object_id = self._group.save(event)
            for hook in self._hooks:
                hook.on_group_message(event, object_id, self._group)
        elif isinstance(event, PrivateMessageEvent):
            object_id = self._private.save(event)
            for hook in self._hooks:
                hook.on_private_message(event, object_id, self._private)

    @property
    def hooks(self) -> Sequence[DatabaseHook]:
        return self._hooks

    def query_group(
        self,
        group_id: int,
        k: Optional[int] = None,
    ) -> Sequence[GroupMessageEvent]:
        return self._group.query({"group_id": group_id}, k)

    def query_private(
        self,
        user_id: int,
        k: Optional[int] = None,
    ) -> Sequence[PrivateMessageEvent]:
        return self._private.query({"user_id": user_id}, k)

    def register_hook(self, hook: Type[TM]) -> TM:
        registered = hook(self.db)
        self._hooks.append(registered)
        return registered

    def find(self, message_id: ObjectId) -> Optional[MessageEvent]:
        event = self._group.get(message_id)
        if event is not None:
            return event
        return self._private.get(message_id)
