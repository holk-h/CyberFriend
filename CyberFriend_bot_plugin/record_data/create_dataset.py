import json
import random
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from GetPathUtil import getPath

def read_prompt_file(prompt_file_path):
    with open(prompt_file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_consecutive_chat_records(data, num_records=15):
    if len(data) < num_records + 1:
        return None, None
    start_index = random.randint(0, len(data) - num_records - 1)
    selected_records = data[start_index:start_index + num_records]
    next_record = data[start_index + num_records]
    return selected_records, next_record

def get_random_user_consecutive_messages(data):
    # 随机选择一个用户ID
    unique_user_ids = list(set([record['user_id'] for record in data]))
    selected_user_id = random.choice(unique_user_ids)
    
    # 筛选出该用户的所有消息
    user_messages = [record for record in data if record['user_id'] == selected_user_id]
    
    # 从用户的消息中随机选择一个连续序列
    if len(user_messages) > 1:
        start_index = random.randint(0, len(user_messages) - 2)
        end_index = start_index + 1
        # 确保是连续消息
        while end_index + 1 < len(user_messages) and user_messages[end_index]['user_id'] == user_messages[end_index + 1]['user_id']:
            end_index += 1
        consecutive_messages = user_messages[start_index:end_index + 1]
    else:
        consecutive_messages = user_messages

    return [msg['message'] for msg in consecutive_messages]

def create_dataset_entry(prompt_content, chat_records, data):
    conversations = [{'role': 'system', 'content': prompt_content}]
    user_conversation = {'role': 'user', 'content': str([{str(record['user_id']): record['message']} for record in chat_records])}
    assistant_messages = get_random_user_consecutive_messages(data)
    assistant_conversation = {'role': 'assistant', 'content': str(assistant_messages)}
    conversations.extend([user_conversation, assistant_conversation])
    return {'conversations': conversations}

def generate_datasets(prompt_file_path, json_file_paths, num_datasets=300):
    datasets = []
    prompt_content = read_prompt_file(prompt_file_path)
    all_data = []

    # 从每个文件中读取数据，并将它们合并
    for json_file_path in json_file_paths:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            all_data.extend(data)  # 合并数据

    for _ in range(num_datasets):
        chat_records, next_record = get_consecutive_chat_records(all_data)
        if chat_records is None or next_record is None:
            break  # 数据不足时结束循环
        dataset_entry = create_dataset_entry(prompt_content, chat_records, all_data)
        datasets.append(dataset_entry)

    return datasets

prompt_file_path = getPath('plugins\cyber_friend\prompt.txt')
json_file_paths = [
    getPath('record_data/536348689_2024-02-04.json'),
    getPath('record_data/536348689_2024-02-08.json'),
]

# 生成数据集
datasets = generate_datasets(prompt_file_path, json_file_paths)

output_file_path = 'combined_train.json'
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(json.dumps(datasets, ensure_ascii=False) + '\n')
