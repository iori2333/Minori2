from pydantic import BaseModel

from minori.utils.database import db
from minori.utils.resource import manager
from .token_db import TokenDatabase


class ResourceTokens(BaseModel):
    where: list[str]
    foods: list[str]
    food_fmts: list[str]
    subjects: list[str]
    subject_fmts: list[str]
    games: list[str]
    game_fmts: list[str]
    forbidden: list[str]
    me: list[str]
    you: list[str]


token_db = db.register_hook(TokenDatabase)
resources = manager.model("ask.tokens", ResourceTokens)
