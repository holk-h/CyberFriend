import random
import re
import time

from nonebot import logger
from nonebot import on_message, get_bots
from nonebot.internal.adapter import Bot, Event

from .utils import GLM
from ..message_record import MessageRecordService

bot = get_bots()
glm = GLM()
messageRecordService = MessageRecordService()
weather = on_message(priority=10, block=True)

def extract_session(text):
    pattern = r"group_(\d+)_\d+"
    match = re.search(pattern, text)
    middle_part = match.group(1) if match else None
    return middle_part

def extract_id(text):
    pattern = r"group_\d+_(\d+)"
    match = re.search(pattern, text)
    third_part = match.group(1) if match else None
    return third_part

def remove_cq_patterns(json_objects):
    pattern = re.compile(r'\[CQ:(?!at).*?\]')
    for obj in json_objects:
        for key in obj.keys():
            obj[key] = re.sub(pattern, '', obj[key])
    
    return json_objects

def glmCall(session_id):
    records = messageRecordService.queryLast(session_id)
    records = [{str(i.user_id): i.message} for i in records]
    records.reverse()
    logger.warning(records)
    return glm.call(records)

SESSION_ID_WHITE_LIST = ['793626723', '647155255', '819281715','494611635']

@weather.handle()
async def handle_function(bot: Bot, event: Event):
    session_id = extract_session(event.get_session_id())
    if session_id in SESSION_ID_WHITE_LIST:
        if event.is_tome() or random.randint(1,10) == 4:
            message = glmCall(session_id)
            if len(message) > 0:
                messageRecordService.addOne(session_id, 0, str(message), time.time())
                await weather.finish(message)
            else:
                await weather.finish()
    else:
        await weather.finish()