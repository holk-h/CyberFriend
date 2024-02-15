import os
import random
import re
import sys
import time
import ast

from nonebot import logger
from nonebot import on_message, get_bots
from nonebot.internal.adapter import Bot, Event
from nonebot.adapters.onebot.v11 import Message

from .utils import GLM
from ..message_record import MessageRecordService, imageRecordService
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from common.MessageBuilder import MessageBuilder

bot = get_bots()
glm = GLM()
messageRecordService = MessageRecordService()
llm_reply = on_message(priority=10, block=False)

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

SESSION_ID_WHITE_LIST = ['647155255', '793626723', '819281715']

IMAGE_PATTERN = ["？", "我不知道", "?"]

@llm_reply.handle()
async def handle_function(bot: Bot, event: Event):
    session_id = extract_session(event.get_session_id())
    if session_id in SESSION_ID_WHITE_LIST:
        if event.is_tome() or random.randint(1,10) == 4:
            message = glmCall(session_id)
            logger.warning(message)
            try:
                for msg in ast.literal_eval(message):
                    logger.warning('msg:::'+msg)
                    if msg in IMAGE_PATTERN:
                        logger.warning('msg:::111'+msg)
                        logger.warning(str(MessageBuilder().appendImage(imageRecordService.getRandomImage()).build()))
                        await llm_reply.send(MessageBuilder().appendImage(imageRecordService.getRandomImage()).build())
                    else:
                        logger.warning('msg:::222'+msg)
                        await llm_reply.send(Message(msg))
            except Exception as e:
                logger.warning(e)
            if len(message) > 0:
                messageRecordService.addOne(session_id, 0, str(message), time.time())
                await llm_reply.finish()
            else:
                await llm_reply.finish()
    else:
        await llm_reply.finish()