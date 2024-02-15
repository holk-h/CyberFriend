from nonebot import get_driver, on_notice, logger
from nonebot.adapters.onebot.v11 import Event, GroupDecreaseNoticeEvent
from nonebot.internal.rule import Rule
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="member_leave",
    description="",
    usage="",
    config=Config,
)

from ..update_members import membersService

global_config = get_driver().config
config = Config.parse_obj(global_config)
async def isGroupDecreaseNoticeEvent(event: Event) -> bool:
    return isinstance(event, GroupDecreaseNoticeEvent)

rule = Rule(isGroupDecreaseNoticeEvent)

member_leave = on_notice(rule=rule)

@member_leave.handle()
async def handle_function(event: GroupDecreaseNoticeEvent):
    # 获取新人的id
    user_id = event.get_user_id()
    # 获取群号
    group_id = event.group_id
    logger.warning(f"member_leave: {group_id} {user_id}")
    membersService.updateEnable(group_id, user_id, False)
    await member_leave.finish()


