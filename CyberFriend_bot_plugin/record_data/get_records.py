import sqlite3
import json
import datetime
import re
import os
import sys

# Add the parent directory to the path to import GetPathUtil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from CyberFriend_bot_plugin.GetPathUtil import getPath

def get_database_path():
    return getPath('plugins\\message_record\\message_record.db')

def execute_query(db_path, target_group_id):
    query = "SELECT user_id, message FROM message_record WHERE group_id = ?"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (target_group_id,))
        return cursor.fetchall()

def clean_messages(rows):
    pattern = r"\[CQ:.*?\]"
    extracted_data = []
    for user_id, message in rows:
        cleaned_message = re.sub(pattern, '', message).strip()
        if cleaned_message:
            extracted_data.append({'user_id': user_id, 'message': cleaned_message})
    return extracted_data

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def ensure_directory_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def extract_and_convert_to_json(db_path, target_group_id):
    rows = execute_query(db_path, target_group_id)
    extracted_data = clean_messages(rows)
    json_data = json.dumps(extracted_data, indent=4, ensure_ascii=False)
    return json_data

def main(target_group_id):
    db_path = get_database_path()
    json_result = extract_and_convert_to_json(db_path, target_group_id)
    output_path = getPath(f'record_data\\{target_group_id}_{datetime.date.today()}.json')
    ensure_directory_exists(output_path)
    save_json(json_result, output_path)

if __name__ == "__main__":
    target_group_id = 536348689
    main(target_group_id)
