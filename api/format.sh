#!/bin/bash
set -e

echo "Running ruff format..."
ruff format .

echo "Running ruff check..."
ruff check . --fix
