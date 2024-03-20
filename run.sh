#!/bin/bash

if ! command -v tmux &> /dev/null; then
    echo "tmux could not be found. Please install tmux."
    exit
fi

PYTHON_CMD=python3
PIP_CMD=pip3
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
fi

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "pip could not be found for $PYTHON_CMD. Please ensure pip is installed."
    exit
fi

tmux new-session -d -s CyberFriendCore "$PYTHON_CMD -m $PIP_CMD install -r ./CyberFriend_LLM_core/requirements.txt; $PYTHON_CMD ./CyberFriend_LLM_core/api_server.py"
echo "API started in a tmux session named CyberFriendCore, use 'tmux attach -t CyberFriendCore' to attach to the session."
tmux new-session -d -s CyberFriendBotPlugin 'cd ./CyberFriend_bot_plugin && '"$PYTHON_CMD"' -m $PIP_CMD install -r requirements.txt && nb run'
echo "CyberFriendBotPlugin started in a tmux session named CyberFriendBotPlugin, use 'tmux attach -t CyberFriendBotPlugin' to attach to the session."

# 避免路径问题，直接创建一个 shell 脚本
cat << 'EOF' > fine_tune_and_restart.sh
#!/bin/bash
PYTHON_CMD=python3
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python
fi
tmux send-keys -t CyberFriendCore C-c
sleep 10
$PYTHON_CMD ./CyberFriend_LLM_core/finetune/finetune_hf.py data/ /chatglm3-6b ./CyberFriend_LLM_core/finetune/configs/configs/lora.yaml
tmux send-keys -t CyberFriendCore "$PYTHON_CMD ./CyberFriend_LLM_core/api_server.py" Enter
EOF

chmod +x fine_tune_and_restart.sh

CRON_JOB="0 4 * * * /absolute/path/to/fine_tune_and_restart.sh"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Setup complete. Fine-tuning and restart scheduled at 4 AM daily."
