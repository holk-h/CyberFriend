import os
import sys

from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import Event
from nonebot.internal.permission import Permission
from nonebot.plugin import PluginMetadata

from .config import Config
from ..message_record import imageRecordService

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from common.CustomChecker import is_me

__plugin_meta__ = PluginMetadata(
    name="add_image_to_db",
    description="",
    usage="",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)

p = Permission(is_me)
add_image_to_db = on_command("addpic", permission=p)

@add_image_to_db.handle()
async def handle_function(event: Event):
    msg = event.get_message()
    images = msg["image"]
    if len(images)>0:
        for img in images:
            imageRecordService.addOne(filePath=img.get('data')['file'], url=img.get('data')['url'])
        add_image_to_db.finish("success:"+str(len(images)))
    else:
        add_image_to_db.finish("请在消息中添加图片")
