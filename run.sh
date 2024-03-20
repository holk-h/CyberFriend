#!/bin/bash

# Ensure tmux is installed
if ! command -v tmux &> /dev/null
then
    echo "tmux could not be found. Please install tmux."
    exit
fi

# Check if python3 and pip3 are available, otherwise use python and pip
PYTHON_CMD=python3
PIP_CMD=pip3
if ! command -v $PYTHON_CMD &> /dev/null
then
    PYTHON_CMD=python
    PIP_CMD=pip
fi

# Verify if pip is accessible via the selected Python command
if ! $PYTHON_CMD -m pip --version &> /dev/null
then
    echo "pip could not be found for $PYTHON_CMD. Please ensure pip is installed."
    exit
fi

echo "Using $PYTHON_CMD for Python commands and $PIP_CMD for pip commands"

# Start the API server in a new tmux session, adapting to the Python and pip commands
tmux new-session -d -s CyberFriend_api_server "$PYTHON_CMD -m $PIP_CMD install -r ./CyberFriend_LLM_core/requirements.txt; $PYTHON_CMD ./CyberFriend_LLM_core/api_server.py"

# Start the bot plugin in another tmux session, adapting to the Python and pip commands
tmux new-session -d -s CyberFriendBot 'cd ./CyberFriend_bot_plugin && '"$PYTHON_CMD"' -m $PIP_CMD install -r requirements.txt && nb run'

echo "Started CyberFriend_api_server and CyberFriendBot in separate tmux sessions, use 'tmux attach -t CyberFriend_api_server' and 'tmux attach -t CyberFriendBot' to view the output of each."
