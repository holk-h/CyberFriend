import os
import re
import sys

from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Event, PrivateMessageEvent
from nonebot.internal.permission import Permission
from nonebot.plugin import PluginMetadata

from .MembersUtil import MembersService, membersService
from .config import Config
from nonebot import logger

__plugin_meta__ = PluginMetadata(
    name="update_members",
    description="",
    usage="",
    config=Config,
)
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from common.CustomChecker import is_me

global_config = get_driver().config
config = Config.parse_obj(global_config)


p = Permission(is_me)
member_update = on_command("update", permission=p)



@member_update.handle()
async def handle_function(event: Event):
    msg: str = event.get_message().__str__()
    # logger.warning("msg:"+msg)
    ans = []
    if msg.strip() != "/update":
        todo = re.split(r"\s+", msg)[1:]
    else:
        todo = ["647155255"]
    # logger.warning("msg:"+str(todo))
    for i in todo:
        tmp = await membersService.updateGroup(i)
        toAp = "OK" if tmp else "FAIL"
        ans.append(i + ":" + toAp)
    await member_update.finish(str(ans))
