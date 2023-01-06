import random
from nonebot import on_fullmatch, on_startswith
from nonebot.adapters.onebot.v11 import Bot, MessageEvent

from minori.utils import Priority
from .parser import parser
from .resources import resources

ask_matcher = on_startswith("问", priority=Priority.Now, block=True)
eat_matcher = on_fullmatch("吃什么", priority=Priority.Now, block=True)
learn_matcher = on_fullmatch("学什么", priority=Priority.Now, block=True)
game_matcher = on_fullmatch("玩什么", priority=Priority.Now, block=True)


@ask_matcher.handle()
async def ask(bot: Bot, event: MessageEvent) -> None:
    reply = await parser.parse(bot, event)
    if reply:
        await ask_matcher.finish(reply)
    else:
        await ask_matcher.finish()


@eat_matcher.handle()
async def eat() -> None:
    food_fmt = random.choice(resources.food_fmts)
    food = random.choice(resources.foods)
    await eat_matcher.finish(food_fmt.format(food))


@learn_matcher.handle()
async def learn() -> None:
    subject_fmt = random.choice(resources.subject_fmts)
    subject = random.choice(resources.subjects)
    await learn_matcher.finish(subject_fmt.format(subject))


@game_matcher.handle()
async def game() -> None:
    game_fmt = random.choice(resources.game_fmts)
    game = random.choice(resources.games)
    await game_matcher.finish(game_fmt.format(game))
