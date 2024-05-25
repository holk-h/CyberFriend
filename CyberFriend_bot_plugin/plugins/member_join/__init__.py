import os
import sys

from nonebot import get_driver, on_notice, get_bots
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, Event
from nonebot.internal.rule import Rule
from nonebot.plugin import PluginMetadata
from nonebot import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from CyberFriend_bot_plugin.GetPathUtil import getPath, BOT_ID
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="member_join",
    description="",
    usage="",
    config=Config,
)

from ..update_members import membersService

global_config = get_driver().config
config = Config.parse_obj(global_config)


async def isGroupIncreaseNoticeEvent(event: Event) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent)

rule = Rule(isGroupIncreaseNoticeEvent)

member_join = on_notice(rule=rule)

@member_join.handle()
async def handle_function(event: GroupIncreaseNoticeEvent):
    # 获取新人的id
    user_id = event.get_user_id()
    # 获取群号
    group_id = event.group_id
    bot = get_bots()[BOT_ID]
    oneData = await bot.call_api("get_group_member_info", group_id=group_id, user_id=user_id)
    logger.warning(oneData)
    mem = membersService.query(group_id,user_id)
    if mem is None:
        membersService.addOne(oneData)
    else:
        membersService.updateOne(oneData, True)
    await member_join.finish()