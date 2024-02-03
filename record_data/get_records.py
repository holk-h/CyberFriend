import sqlite3
import json
import datetime
import re

database_path = 'D:\holk\CyberFriend\plugins\message_record\message_record.db'

def extract_and_convert_to_json(db_path, target_group_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"SELECT user_id, message FROM message_record WHERE group_id = {target_group_id}"
    cursor.execute(query)
    rows = cursor.fetchall()

    # pattern = r"\[CQ:(?!at).*?\]"
    pattern = r"\[CQ:.*?\]"
    extracted_data = []
    for row in rows:
        cleaned_message = re.sub(pattern, '', row[1]).strip()
        if cleaned_message == '':
            continue
        extracted_data.append({'user_id': row[0], 'message': cleaned_message})

    json_data = json.dumps(extracted_data, indent=4, ensure_ascii=False)
    conn.close()

    return json_data

target_group_id = 536348689
json_result = extract_and_convert_to_json(database_path, target_group_id)
with open(f'D:/holk/CyberFriend/record_data/{target_group_id}_{datetime.date.today()}.json', 'w', encoding='utf-8') as f:
    f.write(json_result)
