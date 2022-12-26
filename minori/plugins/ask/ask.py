from nonebot import on_startswith
from nonebot.adapters.onebot.v11 import Bot, MessageEvent

from minori.utils import Priority
from .parser import Parser

matcher = on_startswith("问", priority=Priority.Now, block=True)
parser = Parser()


@matcher.handle()
async def _(bot: Bot, event: MessageEvent):
    reply = await parser.parse(bot, event)
    if reply:
        await matcher.finish(reply)
    else:
        await matcher.finish()
