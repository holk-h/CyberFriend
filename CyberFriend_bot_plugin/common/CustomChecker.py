# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import os
import sys

from nonebot.adapters.onebot.v11 import Event, PrivateMessageEvent, GroupMessageEvent

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from plugins.update_members import membersService


async def is_me(event: Event):
    return ((event.get_user_id() in [mem.user_id for mem in membersService.queryByGroupId(647155255)] and isinstance(event, PrivateMessageEvent))
            or (isinstance(event, GroupMessageEvent) and event.group_id == 647155255))


async def is_private(event: Event):
    return isinstance(event, PrivateMessageEvent)


async def is_group(event: Event):
    return isinstance(event, GroupMessageEvent)


async def is_admin(event: GroupMessageEvent):
    return event.sender.role == "admin"
