from nonebot.rule import to_me
from .utils import GLM
from nonebot import on_message, get_bots
from nonebot.rule import to_me
from nonebot import logger
from nonebot.internal.adapter import Bot, Event
from nonebot.rule import to_me
from ..message_record import MessageRecordService
import re
import random

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

@weather.handle()
async def handle_function(bot: Bot, event: Event):
    records =  messageRecordService.queryLast(extract_session(event.get_session_id()))
    
    # logger.warning(records)
    # logger.warning(event.get_session_id())
    # logger.warning(extract_session(event.get_session_id())
    records = [{str(i.user_id): i.message} for i in records]
    records.reverse()
    
    # logger.warning(records)
    # logger.warning(records[1:].append(str(event.get_message())))
    # logger.warning(extract_session(event.get_session_id()))
    if (extract_session(event.get_session_id()) == '793626723' or extract_session(event.get_session_id()) == '647155255' or extract_session(event.get_session_id()) == '819281715'):
        if random.randint(1,10) == 4:
            # logger.warning(extract_session(event.get_session_id()))
            # records.append({str(extract_id(event.get_session_id())):str(event.get_message())})
            logger.warning(records)
            # logger.warning(event.get_session_id())
            await weather.finish(glm.call(records))
    else:
        await weather.finish()