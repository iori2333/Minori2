import random
from typing import Callable, Optional
import re

from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent

from .resources import resources, token_db

WHERE = re.compile("哪里")
HOW_MUCH = re.compile("多少")
HOW_LONG = re.compile("多久")
WHEN = re.compile("什么时候")
WHAT = re.compile("什么")
WHO = re.compile("谁")
OR = re.compile("还是")
NOT = re.compile(r"(.)(不|没)\1")
PERSON = re.compile(f"({'|'.join(resources.me + resources.you)})")

Pattern = re.Pattern[str]
Match = re.Match[str]


class Parser:

    BasicMappingFunc = Callable[[Match], str]
    GroupMappingFunc = Callable[[Match, list[str]], str]

    def __init__(self) -> None:
        self.basic_mapping: dict[Pattern, Parser.BasicMappingFunc] = {
            HOW_MUCH: self.random_how_much,
            HOW_LONG: self.random_how_long,
            WHEN: self.random_when,
            NOT: self.random_not,
            PERSON: self.replace_person,
        }

        self.group_mapping: dict[Pattern, Parser.GroupMappingFunc] = {
            WHO: self.random_who,
            WHERE: self.random_where,
        }

    @classmethod
    def is_question(cls, message: str) -> bool:
        if any(message.startswith(x) for x in resources.forbidden):
            return False
        return message.startswith("问")

    async def parse(self, bot: Bot, event: MessageEvent) -> Optional[Message]:
        message = event.get_plaintext()
        if not self.is_question(message):
            return None
        raw_message = message[1:]
        raw_message = random.choice(OR.split(raw_message))
        if not raw_message:
            return None
        for reg, func in self.basic_mapping.items():
            raw_message = reg.sub(func, raw_message)

        if isinstance(event, GroupMessageEvent):
            members_ = await bot.get_group_member_list(group_id=event.group_id)
            members: list[str] = [
                member["card"] or member["nickname"] for member in members_
            ]
            for reg, func2 in self.group_mapping.items():
                raw_message = reg.sub(lambda x: func2(x, members), raw_message)

        raw_message = WHAT.sub(lambda _: self.random_what(event), raw_message)
        if not raw_message or raw_message == message:
            return None
        return Message(raw_message)

    def random_how_much(self, _: Match) -> str:
        return str(random.randint(0, 100))

    def random_how_long(self, _: Match) -> str:
        seconds = random.randint(1, 59)
        minutes = random.randint(1, 59)
        hours = random.randint(1, 23)
        return random.choice([f"{seconds}秒", f"{minutes}分钟", f"{hours}小时"])

    def random_when(self, _: Match) -> str:
        h, m = random.randint(0, 23), random.randint(0, 59)
        return f"{h}点{m}分"

    def random_not(self, match: Match) -> str:
        hint = match.group(2)
        text = match.group(1)
        return hint + text if random.random() < 0.5 else text

    def random_who(self, _: Match, members: list[str]) -> str:
        return random.choice(members)

    def random_where(self, _: Match, members: list[str]) -> str:
        where_fmt = random.choice(resources.where)
        person = random.choice(members)
        return where_fmt.format(person)

    def replace_person(self, m: Match) -> str:
        p = m.group(1)
        if p in resources.me:
            return random.choice(resources.you)
        if p in resources.you:
            return random.choice(resources.me)
        return p

    def random_what(self, event: MessageEvent) -> str:
        token = token_db.random(event)
        return token.extract_plain_text() if token else ""


parser = Parser()
