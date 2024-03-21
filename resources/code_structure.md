功能性代码结构和功能说明如下：
```
CyberFriend
├── CyberFriend_LLM_core           # CyberFriend的核心大模型（LLM）部分
│   ├── ChromaRag.py               # RAG 部分
│   ├── api_server.py              # API 服务器
│   ├── download.py                # 用于下载 ChatGLM3 的程序
│   ├── finetune                   # 微调相关的目录，包含配置和微调脚本
│   │   ├── configs                # 微调配置文件存放的位置，使用 lora 即可
│   │   └── finetune_hf.py         # 使用 Hugging Face 库进行微调模型的程序
│   └── utils.py                   # 工具函数
├── CyberFriend_bot_plugin         # CyberFriend 的机器人插件部分
│   ├── GetPathUtil.py             # 获取路径的工具
│   ├── common                     # 公共功能模块，包含各种工具和检查器
│   │   ├── CustomChecker.py       # 自定义检查功能
│   │   ├── MembersOptUtil.py      # 成员操作工具
│   │   └── MessageBuilder.py      # 消息构建器
│   ├── plugins                    # 插件目录，包含各种机器人插件
│   │   ├── add_image_to_db        # 将图片添加到数据库的插件
│   │   ├── cyber_friend           # CyberFriend 核心插件
│   │   │   ├── prompt.txt         # prompt 文本文件
│   │   │   └── utils.py           # 工具脚本
│   │   ├── group_handle           # 群组处理插件
│   │   ├── member_join            # 成员加入处理插件
│   │   ├── member_leave           # 成员离开处理插件
│   │   ├── message_record         # 消息记录插件，包含图像工具、获取记录和其他工具
│   │   │   ├── ImageUtil.py       # 图像处理工具
│   │   │   ├── get_record.py      # 获取记录的脚本
│   │   │   └── util.py            # 通用工具脚本
│   │   ├── scheduler              # 计划任务插件
│   │   └── update_members         # 更新成员信息的插件
│   │       └──  MembersUtil.py    # 成员工具脚本
│   ├── pyproject.toml             # Python项目配置文件
│   └── record_data                # 记录数据的目录
│       ├── create_dataset.py      # 创建数据集的脚本
│       ├── get_records.py         # 获取记录的脚本
│       └── query_number.py        # 查询编号的脚本
├── finetune_and_restart.sh        # 微调模型并重启服务的脚本
└── run.sh                         # 运行 CyberFriend 服务的脚本

```