#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect environment
if [ -f "$SCRIPT_DIR/env/dev/.env" ]; then
    ENV_FILE="$SCRIPT_DIR/env/dev/.env"
    PROJECT="$SCRIPT_DIR/backend"
else
    ENV_FILE="$SCRIPT_DIR/backend/.env"
    PROJECT="$SCRIPT_DIR/backend"
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found"
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

# Docker
if [ -x "/usr/local/bin/python" ]; then
    PYTHON="/usr/local/bin/python"

# Host / venv
else
    PYTHON="$(which python)"
fi

LOG="/tmp/process_commands.log"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: Python not found: $PYTHON"
    exit 1
fi

if [ ! -d "$PROJECT" ]; then
    echo "ERROR: Project directory not found: $PROJECT"
    exit 1
fi

while true
do
    cd "$PROJECT" || exit 1

    "$PYTHON" manage.py process_overdue_scores >> "$LOG" 2>&1
    "$PYTHON" manage.py check_deadlines >> "$LOG" 2>&1
    "$PYTHON" manage.py check_internal_task_deadlines >> "$LOG" 2>&1
    "$PYTHON" manage.py process_internal_task_routines >> "$LOG" 2>&1


    sleep 3
done