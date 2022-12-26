from nonebot import on_command

from minori.utils import Priority

matcher = on_command("ping", block=True, priority=Priority.Urgent)


@matcher.handle()
async def ping() -> None:
    await matcher.finish("Pong!")
