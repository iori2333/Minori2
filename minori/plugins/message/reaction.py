from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent, GroupBanNoticeEvent, MessageSegment

from minori.utils import Priority

tap_matcher = on_type(PokeNotifyEvent, priority=Priority.Default)
mute_matcher = on_type(GroupBanNoticeEvent, priority=Priority.Default)


@tap_matcher.handle()
async def tap(event: PokeNotifyEvent) -> None:
    if not event.is_tome():
        await tap_matcher.finish(
            MessageSegment.poke(event.sub_type, event.get_user_id()))
    await tap_matcher.finish()


@mute_matcher.handle()
async def mute(bot: Bot, event: GroupBanNoticeEvent) -> None:
    if event.is_tome() or event.duration == 0:
        await mute_matcher.finish()
    banner = await bot.get_group_member_info(
        group_id=event.group_id,
        user_id=event.operator_id,
    )
    banner_name: str = banner.get("card", banner["nickname"])

    user = await bot.get_group_member_info(
        group_id=event.group_id,
        user_id=event.user_id,
    )
    user_name: str = user.get("card", user["nickname"])
    await mute_matcher.finish(
        f"{user_name}被万恶的{banner_name}禁言了{event.duration // 60}分钟")
