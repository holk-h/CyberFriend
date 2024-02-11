from peft import PeftModel
from transformers import AutoTokenizer, AutoModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import contextlib
import time
autocast = contextlib.nullcontext
 
# 加载原始 LLM
model_path = "/home/holk/holk_code/ChatGLM3/chatglm3-6b"
 
load_st = time.time()
model = AutoModelForCausalLM.from_pretrained(
model_path, load_in_8bit=False, trust_remote_code=True,
device_map="auto" # 模型不同层会被自动分配到不同GPU上进行计算)
)
load_end = time.time()
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
# 原始 LLM 安装上 Lora 模型
lora_model = PeftModel.from_pretrained(model, "/home/holk/holk_code/ChatGLM3/finetune_demo/output/checkpoint-2500").half()
load_lora_end = time.time()
while True:
    inputText = input("请输入信息 [输入'q'退出]\n")
    if inputText == 'q':
        print("Exit!")
        break
    else:
        time_st = time.time()
        inputs = tokenizer(inputText + "\n", return_tensors='pt')
        inputs = inputs.to('cuda:0')
        time_token = time.time()
        ori_pred = model.generate(**inputs, max_new_tokens=512, do_sample=True)
        ori_answer = tokenizer.decode(ori_pred.cpu()[0], skip_special_tokens=True)
        time_ori = time.time()
        lora_pred = lora_model.generate(**inputs, max_new_tokens=512, do_sample=True)
        lora_answer = tokenizer.decode(lora_pred.cpu()[0], skip_special_tokens=True)
        time_lora = time.time()
        print("原始输出:")
        print(ori_answer)
        print('Lora输出:')
        print(lora_answer)