# -*- coding: utf-8 -*-
from __future__ import annotations

import time
from typing import Type, Union, Any

from nonebot import get_bots
from sqlalchemy import create_engine, Column, Integer, String, Float, update
from sqlalchemy.orm import sessionmaker, declarative_base
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from CyberFriend_bot_plugin.GetPathUtil import getPath, BOT_ID

engine = create_engine('sqlite:///' + getPath("plugins/update_members/members.db"), echo=False)
Base = declarative_base()
session = sessionmaker(bind=engine)()


class Members(Base):
    __tablename__ = 'Members'

    group_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    qq_level = Column(Integer)
    age = Column(Integer)
    sex = Column(Integer)
    nick_name = Column(String)
    name_card = Column(String)
    special_title = Column(String)
    email = Column(String)
    sign = Column(String)
    join_date = Column(Integer)
    last_speak_date = Column(Integer)
    ext_data = Column(String)
    ctime = Column(Integer)
    utime = Column(Integer)
    enable = Column(Integer)

    def __repr__(self):
        return f'<Members(group_id={self.group_id}, user_id={self.user_id}, qq_level={self.qq_level}, age={self.age}, sex={self.sex}, nick_name={self.nick_name}, name_card={self.name_card}, special_title={self.special_title}, email={self.email}, sign={self.sign}, join_date={self.join_date}, last_speak_date={self.last_speak_date}, ext_data={self.ext_data}, ctime={self.ctime}, utime={self.utime}, enable={self.enable})>'


Base.metadata.create_all(engine)


class MembersService:
    def __init__(self, session=session):
        self.session = session
        self.bot = None

    def getSelfBot(self):
        if self.bot is None:
            try:
                self.bot = get_bots()[BOT_ID]
            except ValueError:
                self.bot = None
        return self.bot

    def queryAll(self):
        return self.session.query(Members).all()

    #
    # def querySpecifyAll(self, group_id):
    #     return self.session.query(MessageRecord).filter(MessageRecord.group_id == group_id).all()
    #
    def query(self, group_id, user_id) -> Type[Members] | None:
        try:
            return self.session.query(Members).filter(Members.group_id == group_id, Members.user_id == user_id).one()
        except:
            return None

    def queryByGroupId(self, group_id) -> list[Type[Members]]:
        try:
            return self.session.query(Members).filter(Members.group_id == group_id).all()
        except:
            return []

    def detect(self, group_id, start_time=time.time()):
        mems: list[Type[Members]] = self.queryByGroupId(group_id)
        ans = []
        if mems:
            for mem in mems:
                if len(mem.special_title) == 0 and mem.join_date <= start_time:
                    ans.append(mem.user_id)
        return ans

    def queryByData(self, oneData: dict):
        user_id = oneData.get('user_id')
        group_id = oneData.get('group_id')
        return self.query(group_id, user_id)

    def addOne(self, oneData: dict):
        user_id = oneData.get('user_id')
        group_id = oneData.get('group_id')
        user_name = oneData.get('user_name')
        sex = oneData.get('sex')
        age = oneData.get('age')
        title = oneData.get('title')
        title_expire_time = oneData.get('title_expire_time')
        nickname = oneData.get('nickname')
        user_displayname = oneData.get('user_displayname')
        card = oneData.get('card')
        distance = oneData.get('distance')
        honor = oneData.get('honor')
        join_time = oneData.get('join_time')
        last_active_time = oneData.get('last_active_time')
        last_sent_time = oneData.get('last_sent_time')
        unique_name = oneData.get('unique_name')
        area = oneData.get('area')
        level = oneData.get('level')
        role = oneData.get('role')
        unfriendly = oneData.get('unfriendly')
        card_changeable = oneData.get('card_changeable')
        shut_up_timestamp = oneData.get('shut_up_timestamp')
        messageRecord = Members(group_id=group_id, user_id=user_id, qq_level=level, age=age, sex=sex, nick_name=nickname,
                                name_card=user_displayname, special_title=title, join_date=join_time, last_speak_date=last_sent_time,
                                ctime=int(time.time()), utime=int(time.time()), enable=1)
        session.add(messageRecord)
        session.commit()

    from sqlalchemy import update

    def updateOne(self, oneData: dict, enable=True):
        user_id = oneData.get('user_id')
        group_id = oneData.get('group_id')
        user_name = oneData.get('user_name')
        sex = oneData.get('sex')
        age = oneData.get('age')
        title = oneData.get('title')
        title_expire_time = oneData.get('title_expire_time')
        nickname = oneData.get('nickname')
        user_displayname = oneData.get('user_displayname')
        card = oneData.get('card')
        distance = oneData.get('distance')
        honor = oneData.get('honor')
        join_time = oneData.get('join_time')
        last_active_time = oneData.get('last_active_time')
        last_sent_time = oneData.get('last_sent_time')
        unique_name = oneData.get('unique_name')
        area = oneData.get('area')
        level = oneData.get('level')
        role = oneData.get('role')
        unfriendly = oneData.get('unfriendly')
        card_changeable = oneData.get('card_changeable')
        shut_up_timestamp = oneData.get('shut_up_timestamp')

        # 使用 SQLAlchemy 的 update 语句更新数据
        update_statement = update(Members).where(Members.user_id == user_id, Members.group_id == group_id).values(
            group_id=group_id,
            qq_level=level,
            age=age,
            sex=sex,
            nick_name=nickname,
            name_card=user_displayname,
            special_title=title,
            join_date=join_time,
            last_speak_date=last_sent_time,
            utime=int(time.time()),
            enable=int(enable)
        )

        session.execute(update_statement)
        session.commit()

    def updateEnable(self, group_id, user_id, enable=False):
        update_statement = update(Members).where(Members.user_id == user_id, Members.group_id == group_id).values(
            utime=int(time.time()),
            enable=int(enable)
        )
        session.execute(update_statement)
        session.commit()

    def updateTitle(self, group_id, user_id, title):
        if self.query(group_id, user_id) is not None:
            update_statement = update(Members).where(Members.user_id == user_id, Members.group_id == group_id).values(
                utime=int(time.time()),
                special_title=title
            )
            session.execute(update_statement)
            session.commit()

    async def updateGroup(self, group_id: int or str):
        try:
            if isinstance(group_id, str):
                group_id = int(group_id)
            bot = self.getSelfBot()
            data = await bot.get_group_member_list(group_id=group_id)
            onlineSet = set()
            for oneData in data:
                user_id = oneData.get('user_id')
                group_id = oneData.get('group_id')
                onlineSet.add(str(group_id) + str(user_id))
                mem = self.query(group_id, user_id)
                if mem is None:
                    self.addOne(oneData)
                else:
                    self.updateOne(oneData, True)
            all = self.queryByGroupId(group_id)
            for mem in all:
                user_id = mem.user_id
                group_id = mem.group_id
                key = str(group_id) + str(user_id)
                if key not in onlineSet:
                    d = self.query(group_id, user_id)
                    if d.enable == 1:
                        self.updateEnable(group_id, user_id, False)
            return True
        except Exception as e:
            import traceback
            traceback.print_exception(e)
            return False

membersService = MembersService()

if __name__ == '__main__':
    # membersService = MembersService()
    # print(membersService.queryAll())
    # membersService.addOne({'user_id': 1084701532, 'group_id': 494611635, 'user_name': 'huozhe', 'sex': 'female', 'age': 0, 'title': '', 'title_expire_time': 0, 'nickname': 'huozhe', 'user_displayname': '火者\u2067汪    \u2067\u202d\u202d\u202d', 'card': '火者\u2067汪    \u2067\u202d\u202d\u202d', 'distance': 100, 'honor': [], 'join_time': 1668395651, 'last_active_time': 1706601769, 'last_sent_time': 1706601769, 'unique_name': '', 'area': '', 'level': 10315, 'role': 'owner', 'unfriendly': False, 'card_changeable': True, 'shut_up_timestamp': 0})
    print(membersService.query(536348689, 477751243))
