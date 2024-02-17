import json
import datetime
from util import MessageRecordService

target_group_id = 536348689
path = f'D:\holk\CyberFriend\CyberFriend_bot_plugin\\record_data\{target_group_id}_{datetime.date.today()}.json'
MS = MessageRecordService()

record = MS.querySpecifyAll(target_group_id)
record = [{"user_id": i.user_id, "message": i.message} for i in record]
record.reverse()
filtered_messages = []
for msg in record:
    # cq_index = msg["message"].find("[CQ:forward")
    # if cq_index == -1 or (cq_index != -1 and msg["message"][cq_index:].startswith("[CQ:at")):
    filtered_messages.append(msg)
with open(path, 'w', encoding='utf-8') as f:
    json.dump(filtered_messages, f, indent=4, ensure_ascii=False)