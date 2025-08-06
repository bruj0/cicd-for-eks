#!/bin/bash
set -e

echo "Starting Ping-Pong application..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Files in directory:"
ls -la

# Check if the Flask app can be imported
echo "Testing Flask app import..."
python -c "from wsgi import app; print('Flask app imported successfully')"

# Start with gunicorn
echo "Starting gunicorn..."
exec gunicorn --config gunicorn.conf.py wsgi:app
