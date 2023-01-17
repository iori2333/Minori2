from nonebot import on_type

from minori.adapter import MessageSegment, MessageEvent, Priority
from minori.adapter.event import NudgeEvent, MemberMuteEvent, MemberLeaveEventQuit, MemberJoinEvent
from minori.utils.database import db

from .seg_db import SegmentDatabase

tap_matcher = on_type(NudgeEvent, priority=Priority.Default)
mute_matcher = on_type(MemberMuteEvent, priority=Priority.Default)
welcome_matcher = on_type(MemberJoinEvent, priority=Priority.Default)
leave_matcher = on_type(MemberLeaveEventQuit, priority=Priority.Default)
db_matcher = on_type(MessageEvent, priority=Priority.Default)

seg_database = db.register_hook(SegmentDatabase)


@tap_matcher.handle()
async def tap(event: NudgeEvent) -> None:
    if not event.is_tome():
        await tap_matcher.finish(event.get_message())
    await tap_matcher.finish()


@mute_matcher.handle()
async def mute(event: MemberMuteEvent) -> None:
    if event.is_tome():
        return
    banner = event.operator
    user = event.member
    if banner is None:
        return
    send = f"{user.name}被万恶的{banner.name}禁言了{event.duration_seconds // 60}分钟"
    await mute_matcher.finish(send)


@welcome_matcher.handle()
async def welcome(event: MemberJoinEvent) -> None:
    send = MessageSegment.at(event.member.id)
    send += "欢迎新大佬~"
    await welcome_matcher.finish(send)


@leave_matcher.handle()
async def leave() -> None:
    await leave_matcher.finish(f"有dalao离开了呢...")


@db_matcher.handle()
async def store(event: MessageEvent) -> None:
    db.insert(event)


@db_matcher.handle()
async def load(event: MessageEvent) -> None:
    msg = seg_database.random(event, p=1)
    if msg is not None and msg != event.get_message():
        for seg in msg:
            print(seg, seg.type, seg.data, str(seg))
        await db_matcher.finish(msg)
