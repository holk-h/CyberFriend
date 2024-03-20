#!/bin/bash

# Define the absolute path for the CyberFriend project
PROJECT_DIR=$(pwd)

# Ensure the correct Python command is used
PYTHON_CMD=python3
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python
fi

# Stop the CyberFriendCore session gracefully
tmux send-keys -t CyberFriendCore C-c
sleep 10

# Run the fine-tuning script
$PYTHON_CMD $PROJECT_DIR/CyberFriend_LLM_core/finetune/finetune_hf.py $PROJECT_DIR/data/ /chatglm3-6b $PROJECT_DIR/CyberFriend_LLM_core/finetune/configs/configs/lora.yaml

# Restart the CyberFriendCore session
tmux send-keys -t CyberFriendCore "$PYTHON_CMD $PROJECT_DIR/CyberFriend_LLM_core/api_server.py" Enter