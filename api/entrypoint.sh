#!/bin/bash
set -e

# Create venv at /opt/venv (outside bind mount /app)
if [ ! -f "/opt/venv/bin/pip" ]; then
    echo "Creating virtual environment..."
    python3 -m venv /opt/venv
fi

echo "Installing dependencies..."
cd /app
/opt/venv/bin/pip install --quiet --no-cache-dir -e ".[dev]"

export PATH="/opt/venv/bin:$PATH"

# Drop to non-root user
if [ "$(id -u)" = "0" ]; then
    exec gosu 1000:1000 "$@"
fi

exec "$@"
