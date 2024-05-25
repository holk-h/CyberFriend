import time

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from CyberFriend_bot_plugin.GetPathUtil import getPath

engine = create_engine('sqlite:///'+getPath("plugins/message_record/message_record.db"), echo=False)
Base = declarative_base()
session = sessionmaker(bind=engine)()

class MessageRecord(Base):
    __tablename__ = 'message_record'

    group_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    message = Column(String)
    data_time = Column(Float, primary_key=True)

    def __repr__(self):
        return f'<MessageRecord(group_id={self.group_id}, user_id={self.user_id}, message={self.message}, dt={self.data_time})>'

Base.metadata.create_all(engine)

class MessageRecordService:
    def __init__(self, session=session):
        self.session=session

    def queryAll(self):
        return self.session.query(MessageRecord).all()
    
    def querySpecifyAll(self, group_id):
        return self.session.query(MessageRecord).filter(MessageRecord.group_id==group_id).order_by(MessageRecord.data_time.desc()).all()

    def queryLast(self, group_id):
        return self.session.query(MessageRecord).filter(MessageRecord.group_id==group_id).order_by(MessageRecord.data_time.desc()).limit(15).all()

    def addOne(self,group_id, user_id, message, data_time):
        messageRecord = MessageRecord(group_id=group_id, user_id=user_id, message=message, data_time=data_time)
        session.add(messageRecord)
        session.commit()

if __name__ == '__main__':
    # messageRecordService = MessageRecordService()
    # for i in range(10):
    #     messageRecordService.addOne(2, 2, "adsbbb"+str(i), time.time())
    #     time.sleep(0.1)
    # print(messageRecordService.queryAll())
    # print(messageRecordService.queryLast(2))
    from nonebot.adapters.onebot.v11 import Message, MessageSegment
    message = Message(
        [
            MessageSegment.text("test"),
            MessageSegment.text("test4"),
            MessageSegment.image(r"http://gchat.qpic.cn/gchatpic_new/0/0-0-B8F694B7886F0E94481D91958E8AE31F/0?term=2")
        ]
    )
    for i in message["image"]:
        print(i.get("data"))
        print(i)




