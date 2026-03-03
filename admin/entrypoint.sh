#!/bin/sh
set -e

# Install node_modules into /app (bind mount from ./admin)
# IDE sẽ index được node_modules
if [ ! -d "/app/node_modules" ]; then
    echo "Installing dependencies..."
    npm install --silent
fi

exec "$@"
