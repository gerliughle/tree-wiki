#!/bin/bash

# Exit immediately if a command fails
set -e


echo "Checking for security updates..."
sudo apt update && sudo apt upgrade -y

echo "Starting TreeWiki deployment..."


# 1. Pull the latest code from GitHub/Git
echo "Pulling latest code from Git..."
git pull origin main

# 2. Update dependencies in the virtual environment if requirements changed
if [ -f "requirements.txt" ]; then
    echo "Updating Python packages..."
    venv/bin/pip install -r requirements.txt
fi

# 3. Restart the Gunicorn service
echo "Restarting treewiki systemd service..."
sudo systemctl restart treewiki

# 4. Check status
echo "Deployment complete! Checking service status..."
sudo systemctl status treewiki --no-pager
