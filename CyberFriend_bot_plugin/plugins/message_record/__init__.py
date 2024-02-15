import time

from nonebot import get_driver, get_bots, on_message
from nonebot.plugin import PluginMetadata
from nonebot.internal.adapter import Bot, Event
from nonebot.typing import T_State
from nonebot import logger

from .ImageUtil import imageRecordService
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="message_record",
    description="",
    usage="",
    config=Config,
)

from .util import MessageRecordService

global_config = get_driver().config
config = Config.parse_obj(global_config)

bot = get_bots()
message_record = on_message(rule=None, priority=10, block=False)
messageRecordService = MessageRecordService()
@message_record.handle()
async def handle_function(bot: Bot, event: Event, state: T_State):
    # 获取发送人的 QQ 号
    user_id = event.get_user_id()
    # 获取发送人的昵称
    user_name = event.sender.nickname
    # 获取发送的消息内容
    message = event.get_message()
    for m in message["image"]:
        logger.info(f"{m.get('data')['file']}: {m.get('data')['url']}")
    # 判断是否为群聊消息
    if event.message_type == "group":
        # 获取群聊的 ID
        group_id = event.group_id
        # logger.warning(group_id)
        # 获取群聊的名称
        # group_info = await bot.get_group_info(group_id=group_id)
        # group_name = group_info["group_name"]
        # 输出群聊+人 和 消息内容
        messageRecordService.addOne(group_id, user_id, str(message), time.time())
    else:
        # 输出私聊人 和 消息内容
        messageRecordService.addOne(user_id, user_id, str(message), time.time())
