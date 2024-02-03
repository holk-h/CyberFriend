import json
import random
import os

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

def create_dataset_entry(prompt_content, chat_records, next_record):
    conversations = [{'role': 'system', 'content': prompt_content}]
    user_conversation = {'role': 'user', 'content': str([{str(record['user_id']): record['message']} for record in chat_records])}
    assistant_conversation = {'role': 'assistant', 'content': str(next_record['message'])}
    conversations.extend([user_conversation, assistant_conversation])
    return {'conversations': conversations}

def generate_datasets(prompt_file_path, json_file_path, num_datasets=30000):
    datasets = []
    prompt_content = read_prompt_file(prompt_file_path)

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for _ in range(num_datasets):
        chat_records, next_record = get_consecutive_chat_records(data)
        if chat_records is None or next_record is None:
            break  # 数据不足时结束循环
        dataset_entry = create_dataset_entry(prompt_content, chat_records, next_record)
        datasets.append(dataset_entry)

    return datasets

# 文件路径
prompt_file_path = 'D:\holk\CyberFriend\plugins\cyber_friend\prompt.txt'
json_file_path = 'D:/holk/CyberFriend/record_data/536348689_2024-02-03.json'  # 替换为你的 JSON 文件路径

# 生成数据集
datasets = generate_datasets(prompt_file_path, json_file_path)

# 打印或以其他方式使用 datasets
with open(json_file_path.replace('.json', '_train.json'), 'w', encoding='utf-8') as f:
    # for dataset_entry in datasets:
    f.write(json.dumps(datasets, ensure_ascii=False) + '\n')
