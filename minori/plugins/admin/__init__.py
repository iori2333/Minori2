from typing import Sequence
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.mirai2.message import MessageType
from minori.adapter import Priority, Message, Event
from minori.adapter.permission import admin_permission, get_permission, session_of
from minori.utils.resource import manager

matcher = on_command(
    "_permission",
    permission=admin_permission,
    priority=Priority.Urgent,
    block=True,
)
permission_conf = get_permission()

async def _session(args: Sequence[str], event: Event):
    if not args:
        session = session_of(event)
    else:
        session = args[0]
    if session is None:
        await matcher.finish("无法获取会话")
    return session

async def _permit_handler(args: Sequence[str], event: Event):
    session = await _session(args, event)
    permission_conf.allowed_sessions.add(session)
    manager.save_model(permission_conf, "permission")
    await matcher.finish(f"已允许会话 {session} 发送命令")


async def _remove_handler(args: Sequence[str], event: Event):
    session = await _session(args, event)
    permission_conf.allowed_sessions.remove(session)
    manager.save_model(permission_conf, "permission")
    await matcher.finish(f"已移除会话 {session} 的命令权限")

async def _ban_handler(args: Sequence[str], event: Event):
    if not args:
        user = event.get_user_id()
    else:
        user = args[0]
    permission_conf.banned_senders.add(user)
    manager.save_model(permission_conf, "permission")
    await matcher.finish(f"已禁止用户 {user} 发送命令")

async def _unban_handler(args: Sequence[str], event: Event):
    if not args:
        await matcher.finish()
    else:
        user = args[0]
    permission_conf.banned_senders.remove(user)
    manager.save_model(permission_conf, "permission")
    await matcher.finish(f"已移除用户 {user} 的命令禁止")

async def _debug_handler(args: Sequence[str], event: Event):
    session = await _session(args, event)
    permission_conf.debug_sessions.add(session)
    manager.save_model(permission_conf, "permission")
    await matcher.finish(f"已允许会话 {session} 发送调试命令")

async def _undebug_handler(args: Sequence[str], event: Event):
    session = await _session(args, event)
    permission_conf.debug_sessions.remove(session)
    manager.save_model(permission_conf, "permission")
    await matcher.finish(f"已移除会话 {session} 的调试命令权限")

async def _list_handler(args: Sequence[str], event: Event):
    await matcher.finish(
        f"Command Permission:\n"
        f"  allowed sessions: {permission_conf.allowed_sessions}\n"
        f"  banned_users: {permission_conf.banned_senders}\n"
        f"  debug_permissions: {permission_conf.debug_sessions}"
    )

@matcher.handle()
async def handle_permission(event: Event, command: Message = CommandArg()):
    args = []
    for seg in command:
        command.extract_plain_text
        if seg.type == MessageType.AT:
            args.append(str(seg.data["target"]))
        elif seg.is_text():
            text = str(seg).strip()
            args.extend(text.split())
    print(args)
    if not args:
        await matcher.finish()
    match args[0]:
        case "permit":
            await _permit_handler(args[1:], event)
        case "remove":
            await _remove_handler(args[1:], event)
        case "ban":
            await _ban_handler(args[1:], event)
        case "unban":
            await _unban_handler(args[1:], event)
        case "debug":
            await _debug_handler(args[1:], event)
        case "undebug":
            await _undebug_handler(args[1:], event)
        case "list":
            await _list_handler(args[1:], event)
        case _ as cmd:
            await matcher.finish(f"未知命令: {cmd}")
