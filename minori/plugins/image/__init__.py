import random

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.log import logger

from minori.adapter import Event, Bot

from .setu import Setu

setu_matcher = on_command("色图", aliases={"涩图"}, block=True)


@setu_matcher.handle()
async def handle_setu(event: Event, state: T_State):
    message = event.get_plaintext()
    keywords = message.split()
    state["keywords"] = keywords


@setu_matcher.got("keywords")
async def keyword_handler(bot: Bot, event: Event, state: T_State):
    keywords = state["keywords"]
    keyword = random.choice(keywords) if keywords else ""
    try:
        send = Setu.keyword(keyword)
        await bot.send(event=event, message=send)
    except Exception as e:
        logger.error(f"Error sending image: {e.__class__.__name__} {e}")
        await setu_matcher.finish("出错了喵...")
    else:
        await setu_matcher.finish()
