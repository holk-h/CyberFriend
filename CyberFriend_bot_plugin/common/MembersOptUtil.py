# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from plugins.update_members import membersService


def get_normal_member_str(group_id, user_id):
    mem = membersService.query(group_id, user_id)
    if mem is None:
        return str(user_id)
    elif len(mem.name_card.strip())!=0:
        return mem.name_card
    else:
        return mem.nick_name