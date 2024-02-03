import sqlite3
import json
import datetime
import re  # 导入正则表达式库

# 替换为你的数据库文件路径
database_path = 'D:\holk\CyberFriend\plugins\message_record\message_record.db'

def extract_and_convert_to_json(db_path, target_group_id):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 编写 SQL 查询，以筛选具有指定 group_id 的所有行
    query = f"SELECT user_id, message FROM message_record WHERE group_id = {target_group_id}"
    cursor.execute(query)
    rows = cursor.fetchall()

    # 处理每个 message 字段，移除 "[CQ:" 开头，"]" 结尾的部分
    # pattern = r"\[CQ:(?!at).*?\]"
    pattern = r"\[CQ:.*?\]"
    extracted_data = []
    for row in rows:
        cleaned_message = re.sub(pattern, '', row[1]).strip()
        if cleaned_message == '':
            continue
        extracted_data.append({'user_id': row[0], 'message': cleaned_message})

    # 使用 indent 参数格式化 JSON
    json_data = json.dumps(extracted_data, indent=4, ensure_ascii=False)

    # 关闭数据库连接
    conn.close()

    return json_data

# 使用示例
target_group_id = 536348689  # 你要筛选的 group_id 的值
json_result = extract_and_convert_to_json(database_path, target_group_id)
with open(f'D:/holk/CyberFriend/record_data/{target_group_id}_{datetime.date.today()}.json', 'w', encoding='utf-8') as f:
    f.write(json_result)  # 已经格式化，直接写入
