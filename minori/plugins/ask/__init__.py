import random
from nonebot import on_fullmatch, on_startswith

from minori.adapter import Bot, MessageEvent, Priority, default_permission

from .question_parser import Parser
from .resources import tokens

ask_matcher = on_startswith(
    "问",
    priority=Priority.Now,
    block=True,
    permission=default_permission,
)

eat_matcher = on_fullmatch(
    "吃什么",
    priority=Priority.Now,
    block=True,
    permission=default_permission,
)

learn_matcher = on_fullmatch(
    "学什么",
    priority=Priority.Now,
    block=True,
    permission=default_permission,
)

game_matcher = on_fullmatch(
    "玩什么",
    priority=Priority.Now,
    block=True,
    permission=default_permission,
)

parser = Parser()


@ask_matcher.handle()
async def ask(bot: Bot, event: MessageEvent) -> None:
    reply = await parser.parse(bot, event)
    if reply:
        await ask_matcher.finish(reply)
    else:
        await ask_matcher.finish()


@eat_matcher.handle()
async def eat() -> None:
    food_fmt = random.choice(tokens.food_fmts)
    food = random.choice(tokens.foods)
    await eat_matcher.finish(food_fmt.format(food))


@learn_matcher.handle()
async def learn() -> None:
    subject_fmt = random.choice(tokens.subject_fmts)
    subject = random.choice(tokens.subjects)
    await learn_matcher.finish(subject_fmt.format(subject))


@game_matcher.handle()
async def game() -> None:
    game_fmt = random.choice(tokens.game_fmts)
    game = random.choice(tokens.games)
    await game_matcher.finish(game_fmt.format(game))
