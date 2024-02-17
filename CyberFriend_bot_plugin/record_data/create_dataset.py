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
    if len(data) <= num_records:
        return None, None
    start_index = random.randint(0, len(data) - num_records - 1)
    selected_records = data[start_index:start_index + num_records]
    
    # 检查以确保 next_record_index 在数据范围内
    next_record_index = start_index + num_records
    if next_record_index >= len(data):
        return selected_records, None  # 如果越界，就返回无assistant回复

    next_user_id = data[next_record_index]['user_id']
    assistant_messages = [data[next_record_index]['message']]
    
    # 向后查找连续消息
    for i in range(next_record_index + 1, len(data)):
        if data[i]['user_id'] == next_user_id:
            assistant_messages.append(data[i]['message'])
        else:
            break

    return selected_records, assistant_messages

def create_dataset_entry(prompt_content, chat_records, assistant_messages):
    conversations = [{'role': 'system', 'content': prompt_content}]
    user_conversation = {
        'role': 'user', 
        'content': str([{str(record['user_id']): record['message']} for record in chat_records])
    }
    assistant_conversation = {
        'role': 'assistant', 
        'content': str(assistant_messages)
    }
    conversations.extend([user_conversation, assistant_conversation])
    return {'conversations': conversations}

def generate_datasets(prompt_file_path, json_file_paths, num_datasets=180000):
    datasets = []
    prompt_content = read_prompt_file(prompt_file_path)
    all_data = []

    for json_file_path in json_file_paths:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            all_data.extend(data)

    while len(datasets) < num_datasets and len(all_data) > 0:
        chat_records, assistant_messages = get_consecutive_chat_records(all_data)
        if chat_records is None or assistant_messages is None:
            continue  # 跳过这次循环迭代，不添加当前的数据集条目
        dataset_entry = create_dataset_entry(prompt_content, chat_records, assistant_messages)
        datasets.append(dataset_entry)
        # 为了避免重复处理相同的记录，这里可以根据需要调整all_data的裁剪逻辑

    return datasets

prompt_file_path = getPath('plugins\cyber_friend\prompt.txt')
json_file_paths = [getPath('record_data/536348689_2024-02-15.json'),getPath('record_data/793626723_2024-02-15.json')]

# 生成数据集
datasets = generate_datasets(prompt_file_path, json_file_paths)

# 保存生成的数据集
output_file_path = 'train.json'
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(json.dumps(datasets, ensure_ascii=False) + '\n')
