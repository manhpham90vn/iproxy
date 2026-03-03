#!/bin/bash
set -e

echo "Running prettier..."
npm run format

echo "Running eslint..."
npm run lint -- --fix
