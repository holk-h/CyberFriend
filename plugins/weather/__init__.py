from nonebot.rule import to_me
from .utils import GLM
from nonebot import on_message, get_bots
from nonebot.rule import to_me
from nonebot import logger
from nonebot.internal.adapter import Bot, Event
from nonebot.rule import to_me
from nonebot import require
require("nonebot_plugin_chatrecorder")
from nonebot_plugin_chatrecorder import get_message_records
from nonebot_plugin_session import extract_session, SessionIdType
from datetime import datetime, timedelta

bot = get_bots()
glm = GLM()
weather = on_message(rule=to_me(), priority=10, block=True)

@weather.handle()
async def handle_function(bot: Bot, event: Event):
    session = extract_session(bot, event)
    records = await get_message_records(
        session=session,
        time_start=datetime.utcnow() - timedelta(days=1),
    )
    records = records[-15:]
    records = [i.message[0]['data']['text'] for i in records]
    logger.warning(records)
    await weather.finish(glm.call(records, str(event.get_message())))