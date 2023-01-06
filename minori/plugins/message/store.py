from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot import on_type

from minori.utils import Priority
from minori.utils.database import db
from .seg_db import SegmentDatabase

seg_db = db.register_hook(SegmentDatabase)

matcher = on_type(MessageEvent, priority=Priority.Default)


@matcher.handle()
async def store(event: MessageEvent) -> None:
    db.insert(event)


@matcher.handle()
async def load(event: MessageEvent) -> None:
    msg = seg_db.random(event, p=0.1)
    if msg is not None and msg != event.message:
        await matcher.finish(msg)
