# -*- coding: utf-8 -*-
from base64 import b64encode

from nonebot.adapters.onebot.v11 import Message


class MessageBuilder:

    def __init__(self, msg=""):
        self.message = msg

    def appendAt(self, user_id, name=None):
        """尽量随便加个name，不然可能会出现一个名字需要10s超时失败的查询"""
        if name is None:
            self.message += "[CQ:at,qq=" + str(user_id) + ",name=" + user_id + "]"
        else:
            self.message += "[CQ:at,qq=" + str(user_id) + ",name=" + name + "]"
        return self

    def appendText(self, msg):
        self.message += msg
        return self

    def appendImage(self, file: str):
        """支持本地文件/URL/base64字符串"""
        if isinstance(file, str) and not file.startswith("http") and not file.startswith("base64"):
            with open(file, "rb") as f:
                file = f"base64://{b64encode(f.read()).decode()}"
        self.message += f"[CQ:image,file={file},cache=true,proxy=true]"
        return self

    def build(self):
        return Message(self.message)
