from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent


def get_session(event: MessageEvent) -> int:
    if isinstance(event, GroupMessageEvent):
        return event.group_id
    elif isinstance(event, PrivateMessageEvent):
        return event.user_id
    else:
        raise TypeError("Unsupported event type")
