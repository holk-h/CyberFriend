#!/bin/bash

# Define the absolute path for the CyberFriend project. Adjust this as needed.
PROJECT_DIR=$(pwd)

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux could not be found. Please install tmux."
    exit 1
fi

# Determine the correct Python and pip commands
PYTHON_CMD=python3
PIP_CMD=pip3
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
fi

# Ensure pip is installed for the determined Python command
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "pip could not be found for $PYTHON_CMD. Please ensure pip is installed."
    exit 1
fi

# Navigate to the project directory
cd $PROJECT_DIR

# Start the CyberFriendCore session
tmux new-session -d -s CyberFriendCore "$PYTHON_CMD -m $PIP_CMD install -r $PROJECT_DIR/CyberFriend_LLM_core/requirements.txt; $PYTHON_CMD $PROJECT_DIR/CyberFriend_LLM_core/api_server.py"
echo "API started in a tmux session named CyberFriendCore, use 'tmux attach -t CyberFriendCore' to attach to the session."

# Start the CyberFriendBotPlugin session
tmux new-session -d -s CyberFriendBotPlugin "cd $PROJECT_DIR/CyberFriend_bot_plugin && $PYTHON_CMD -m $PIP_CMD install -r requirements.txt && nb run"
echo "CyberFriendBotPlugin started in a tmux session named CyberFriendBotPlugin, use 'tmux attach -t CyberFriendBotPlugin' to attach to the session."

# Schedule the cron job for daily execution at 4 AM
CRON_JOB="0 4 * * * $PROJECT_DIR/finetune_and_restart.sh"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Setup complete. Fine-tuning and restart scheduled at 4 AM daily."
