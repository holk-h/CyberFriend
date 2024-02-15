# -*- coding: utf-8 -*-
import os
import random
import re
import sys
import uuid
from base64 import b64encode

import requests
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from GetPathUtil import getPath

engine = create_engine('sqlite:///' + getPath("plugins/message_record/image_record.db"), echo=False)
Base = declarative_base()
session = sessionmaker(bind=engine)()


class ImageRecord(Base):
    __tablename__ = 'image_record'

    file_name = Column(String, primary_key=True)
    file_url = Column(String)
    file_base64 = Column(String)

    def __repr__(self):
        return f'<ImageRecord(file_name={self.file_name}, file_url={self.file_url}, file_base64={self.file_base64})>'


Base.metadata.create_all(engine)


def get_file_name(file=None, url=None):
    # if the file is a url, extract the last part after the slash
    file_name = ""
    if file is not None:
        file_name = os.path.basename(file)
    if len(file_name) == 0 and url is not None:
        us = url.split("/")
        file_name = us[-1]
        if len(us[-1])<5 and len(us)>1:
            file_name = us[-2]
    if len(file_name) < 5:
        file_name = uuid.uuid4().hex
    # replace any special characters in the file name with underscores
    file_name = re.sub("[^a-zA-Z0-9.]", "_", file_name)
    return file_name


def download_file(url, name):
    file_name = name
    if file_name is None or len(file_name) < 5:
        file_name = get_file_name(file_name, url=url)
    response = requests.get(url)
    # check if the response is successful
    if response.status_code == 200:
        # open a file with the same name as the url
        with open(file_name, "wb") as f:
            # write the response content to the file
            f.write(response.content)
        # return the file name
        return file_name
    else:
        # raise an exception if the response is not successful
        raise Exception(f"Failed to download file from {url}")


class ImageRecordService:
    def __init__(self, session=session):
        self.session = session

    def queryAllName(self):
        return self.session.query(ImageRecord.file_name).all()

    def queryAll(self):
        return self.session.query(ImageRecord).all()

    def queryByName(self, file_name):
        try:
            ans = self.session.query(ImageRecord).filter(ImageRecord.file_name == file_name).one()
        except:
            ans = None
        return ans

    def addOne(self, filePath, url=None):
        """
        本地文件仅传filePath, 网络文件 请传filePath：文件名(可以是None)，url: 下载地址
        """
        name = get_file_name(filePath, url)
        if self.queryByName(name) is None:
            file_url = filePath
            if url is not None:
                file_url = url
                filePath = download_file(url, name)
            try:
                with open(filePath, "rb") as f:
                    file_base64 = f"base64://{b64encode(f.read()).decode()}"
                imageRecord = ImageRecord(file_name=name, file_base64=file_base64, file_url=file_url)
                session.add(imageRecord)
                session.commit()
            finally:
                # 删除自动下载的网络文件
                if os.path.exists(filePath) and url is not None:
                    os.remove(filePath)

    def getRandomImage(self):
        all = self.queryAllName()
        r = random.randint(0, len(all)-1)
        return self.queryByName(all[r][0]).file_base64

imageRecordService = ImageRecordService()

if __name__ == '__main__':
    imageRecordService.addOne(r"F:\Pictures\temp\QQ截图20240215142045.jpg")
    imageRecordService.addOne(filePath=None, url="https://tianquan.gtimg.cn/nudgeaction/item/0/expression.jpg")
    print(imageRecordService.queryAllName())
    print(imageRecordService.getRandomImage())
