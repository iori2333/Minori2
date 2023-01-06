import random

from nonebot import on_command

from minori.utils import Priority

matcher = on_command("ping", block=True, priority=Priority.Urgent)
replies = ['pong!', '我还在睡喵...', 'Zzzz...']


@matcher.handle()
async def ping() -> None:
    await matcher.finish(random.choice(replies))
