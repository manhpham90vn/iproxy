#!/bin/bash
set -e

echo "Running ruff format..."
./venv/bin/ruff format .

echo "Running ruff check..."
./venv/bin/ruff check . --fix
