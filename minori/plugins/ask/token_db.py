from datetime import datetime
import random
from typing import Optional, TypedDict
from typing_extensions import override
from bson import ObjectId
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection as MongoCollection

from minori.adapter import (
    Message,
    MessageEvent,
    GroupMessageEvent,
    FriendMessageEvent,
)
from minori.utils import DatabaseHook, Collection


class Token(TypedDict):
    created_at: datetime
    message: str
    session_id: int


class TokenDatabase(DatabaseHook):

    def __init__(self, db: MongoDatabase) -> None:
        super().__init__(db)
        self._group: MongoCollection[Token] = db.tok_group
        self._private: MongoCollection[Token] = db.tok_private
        self._group.create_index("created_at",
                                 expireAfterSeconds=3600 * 24 * 30)
        self._private.create_index("created_at",
                                   expireAfterSeconds=3600 * 24 * 30)

    def session(
        self,
        event: MessageEvent,
    ) -> tuple[int, MongoCollection[Token]]:
        if isinstance(event, GroupMessageEvent):
            return event.sender.group.id, self._group
        elif isinstance(event, FriendMessageEvent):
            return event.sender.id, self._private
        else:
            raise TypeError("Unsupported event type")

    @override
    def on_group_message(
        self,
        event: GroupMessageEvent,
        inserted: ObjectId,
        _: Collection[GroupMessageEvent],
    ) -> None:
        msg = event.get_message()
        is_text = any(m.is_text() for m in msg)
        text = msg.extract_plain_text()
        if is_text and len(text) < 10:
            token = Token(
                created_at=datetime.now(),
                message=text,
                session_id=event.sender.group.id,
            )
            self._group.insert_one(token)

    @override
    def on_private_message(
        self,
        event: FriendMessageEvent,
        inserted: ObjectId,
        _: Collection[FriendMessageEvent],
    ) -> None:
        msg = event.get_message()
        is_text = any(m.is_text() for m in msg)
        text = msg.extract_plain_text()
        if is_text and len(text) < 10:
            token = Token(
                created_at=datetime.now(),
                message=text,
                session_id=event.sender.id,
            )
            self._private.insert_one(token)

    def random(self, event: MessageEvent) -> Optional[Message]:
        session_id, collection = self.session(event)
        tokens = list(collection.find({"session_id": session_id}))

        if not tokens:
            return None
        token = random.choice(tokens)
        return Message(token["message"])
