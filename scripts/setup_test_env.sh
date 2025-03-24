#!/bin/bash

# Exit on error
set -e

# Set Django settings module
export DJANGO_SETTINGS_MODULE=sail_backend.test_settings

# Set test environment variables
export SECRET_KEY="test-secret-key"
export DEBUG="False"
export DATABASE_URL="sqlite:///:memory:"
export REDIS_URL="redis://localhost:6379/0"
export OPENROUTER_API_KEY="test-key"
export ALLOWED_HOSTS="*"

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install test dependencies if needed
pip install -r requirements.txt

# Run the deployment checks
python scripts/check_deployment.py 