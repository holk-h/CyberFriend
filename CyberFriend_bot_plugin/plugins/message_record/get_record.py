import json
import datetime
from util import MessageRecordService

target_group_id = 793626723
path = f'D:\holk\CyberFriend\CyberFriend_bot_plugin\\record_data\{target_group_id}_{datetime.date.today()}.json'
MS = MessageRecordService()

record = MS.querySpecifyAll(target_group_id)
record = [{"user_id": i.user_id, "message": i.message} for i in record]
with open(path, 'w', encoding='utf-8') as f:
    json.dump(record, f, indent=4, ensure_ascii=False)