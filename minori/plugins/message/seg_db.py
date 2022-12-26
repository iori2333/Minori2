import random
from typing import Optional, Sequence, TypedDict
from typing_extensions import override
from datetime import datetime

from bson import ObjectId
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection as MongoCollection
from jieba import posseg

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageEvent, Message
from nonebot.log import logger

from minori.utils import DatabaseHook, Collection
from minori.utils.database import db

FLAGS = {"n", "s", "nw", "nt", "v", "nz", "l"}


class Segment(TypedDict):
    word1: str
    word2: str
    created_at: datetime
    message_id: ObjectId
    session_id: int


class SegmentDatabase(DatabaseHook):

    def __init__(self, db: MongoDatabase) -> None:
        super().__init__(db)
        self._group: MongoCollection[Segment] = db.seg_group
        self._private: MongoCollection[Segment] = db.seg_private
        self._group.create_index("created_at", expireAfterSeconds=86400 * 7)
        self._private.create_index("created_at", expireAfterSeconds=86400 * 15)

    def cut_insert(self, event: MessageEvent, inserted: ObjectId) -> None:
        words = self.cut(event)
        if len(words) < 2:
            return
        word1, word2 = random.sample(words, k=2)
        session_id, collection = self.session(event)
        segment = Segment(
            word1=word1,
            word2=word2,
            message_id=inserted,
            session_id=session_id,
            created_at=datetime.now(),
        )
        collection.insert_one(segment)

    @override
    def on_group_message(
        self,
        event: GroupMessageEvent,
        inserted: ObjectId,
        _: Collection[GroupMessageEvent],
    ) -> None:
        self.cut_insert(event, inserted)

    @override
    def on_private_message(
        self,
        event: PrivateMessageEvent,
        inserted: ObjectId,
        _: Collection[PrivateMessageEvent],
    ) -> None:
        self.cut_insert(event, inserted)

    @staticmethod
    def cut(event: MessageEvent) -> Sequence[str]:
        return [
            word for word, flag in posseg.cut(event.get_plaintext())
            if flag in FLAGS
        ]

    def session(
        self,
        event: MessageEvent,
    ) -> tuple[int, MongoCollection[Segment]]:
        if isinstance(event, GroupMessageEvent):
            return event.group_id, self._group
        elif isinstance(event, PrivateMessageEvent):
            return event.user_id, self._private
        else:
            raise TypeError("Unsupported event type")

    def random(self, event: MessageEvent, p: float = 0.1) -> Optional[Message]:
        if random.random() > p:
            return None
        words = self.cut(event)
        session_id, collection = self.session(event)
        segments = list(
            collection.find({
                "word1": {
                    "$in": words
                },
                "word2": {
                    "$in": words
                },
                "session_id": session_id
            }))
        if not segments:
            return None
        segment = random.choice(segments)
        found = db.find(segment["message_id"])
        return found.get_message() if found else None
