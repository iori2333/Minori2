from datetime import datetime
import random
from typing import Optional, TypedDict
from typing_extensions import override
from bson import ObjectId
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection as MongoCollection

from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from minori.utils import DatabaseHook, Collection
from minori.utils.database import db


class Token(TypedDict):
    created_at: datetime
    message_id: ObjectId
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
            return event.group_id, self._group
        elif isinstance(event, PrivateMessageEvent):
            return event.user_id, self._private
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
        n = len(msg.extract_plain_text())
        if is_text and n < 10:
            token = Token(
                created_at=datetime.now(),
                message_id=inserted,
                session_id=event.group_id,
            )
            self._group.insert_one(token)

    @override
    def on_private_message(
        self,
        event: PrivateMessageEvent,
        inserted: ObjectId,
        _: Collection[PrivateMessageEvent],
    ) -> None:
        msg = event.get_message()
        is_text = any(m.is_text() for m in msg)
        n = len(msg.extract_plain_text())
        if is_text and n < 10:
            token = Token(
                created_at=datetime.now(),
                message_id=inserted,
                session_id=event.user_id,
            )
            self._private.insert_one(token)

    def random(self, event: MessageEvent) -> Optional[Message]:
        session_id, collection = self.session(event)
        tokens = list(collection.find({"session_id": session_id}))

        if not tokens:
            return None
        token = random.choice(tokens)
        message = db.find(token["message_id"])
        return message.get_message() if message is not None else None