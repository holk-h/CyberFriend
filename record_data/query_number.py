import sqlite3
import datetime

database_path = 'D:\holk\CyberFriend\plugins\message_record\message_record.db'

def count_messages(db_path, target_group_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM message_record WHERE group_id = {target_group_id}"
    cursor.execute(query)
    count = cursor.fetchone()[0]

    conn.close()

    return count

target_group_id = 793626723
message_count = count_messages(database_path, target_group_id)
print(f"Group ID {target_group_id} has {message_count} messages recorded.")
