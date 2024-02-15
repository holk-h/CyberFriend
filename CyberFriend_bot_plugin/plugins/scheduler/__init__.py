import os
import sys

import nonebot
from nonebot import get_driver
from nonebot import logger
from nonebot import require
from nonebot.plugin import PluginMetadata

from .config import Config
from ..update_members import membersService
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from GetPathUtil import getPath, BOT_ID

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

__plugin_meta__ = PluginMetadata(
    name="scheduler",
    description="",
    usage="",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)


# 基于装饰器的方式
@scheduler.scheduled_job("cron", hour="3", minute="0", second="0", id="job_0")
async def update():
    bot = nonebot.get_bots()[BOT_ID]
    data = await bot.call_api("get_group_list")
    groups = [one["group_id"] for one in data]
    logger.info(f"start scheduled_job update {groups}")
    for g_id in groups:
        await membersService.updateGroup(g_id)

