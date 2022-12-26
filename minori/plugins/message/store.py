from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot import on_type

from minori.utils import Priority
from minori.utils.database import db
from .seg_db import SegmentDatabase

seg_db = db.register_hook(SegmentDatabase)

matcher = on_type(MessageEvent, priority=Priority.Default)


@matcher.handle()
async def store(event: MessageEvent):
    db.insert(event)
    await matcher.finish()


@matcher.handle()
async def random(bot: Bot, event: MessageEvent):
    msg = seg_db.random(event, p=0.1)
    if msg is not None:
        await bot.send(event, msg)
        return
    await matcher.finish()
