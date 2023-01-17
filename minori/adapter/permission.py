from typing import Optional
from nonebot import get_driver
from nonebot.permission import Permission
from nonebot.adapters import Bot, Event
from pydantic import BaseModel

from minori.utils.resource import manager
from nonebot.adapters.mirai2.event import (
    MessageEvent,
    GroupMessage as GroupMessageEvent,
)


class PermissionState(BaseModel):
    admins: set[str]
    allowed_sessions: set[str]
    banned_senders: set[str]
    debug_sessions: set[str]

    @staticmethod
    def default() -> "PermissionState":
        return PermissionState(
            admins=set(),
            allowed_sessions=set(),
            banned_senders=set(),
            debug_sessions=set(),
        )


driver = get_driver()
_permission_conf: Optional[PermissionState] = None


def get_permission() -> PermissionState:
    global _permission_conf
    if _permission_conf is not None:
        return _permission_conf
    try:
        _permission_conf = manager.model("permission", PermissionState)
    except FileNotFoundError:
        _permission_conf = PermissionState.default()
    return _permission_conf


permission_conf = get_permission()


def session_of(event: Event) -> Optional[str]:
    if not isinstance(event, MessageEvent):
        return None
    if isinstance(event, GroupMessageEvent):
        return str(event.sender.group.id)
    return str(event.sender.id)


async def session_checker(bot: Bot, event: Event) -> bool:
    session = session_of(event)
    if session is None:
        return True
    return session in permission_conf.allowed_sessions or session in permission_conf.debug_sessions


async def debug_session_checker(bot: Bot, event: Event) -> bool:
    session = session_of(event)
    if session is None:
        return True
    return session in permission_conf.debug_sessions


async def sender_checker(bot: Bot, event: Event) -> bool:
    return event.get_user_id() not in permission_conf.banned_senders


async def admin_checker(bot: Bot, event: Event) -> bool:
    user = event.get_user_id()
    return user in bot.config.superusers or user in permission_conf.admins


default_permission = Permission(session_checker) | sender_checker
admin_permission = Permission(admin_checker)
debug_permission = Permission(debug_session_checker)
