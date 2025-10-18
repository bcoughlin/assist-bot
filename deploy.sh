#!/bin/bash

# Discord-Poe-POC Deployment Script

echo "🚀 Deploying Discord-Poe-POC to Modal..."

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null; then
    echo "❌ Modal CLI not found. Installing..."
    pip install modal
    echo "✅ Modal CLI installed"
fi

# Check if Modal is set up
if ! modal config show &> /dev/null; then
    echo "⚙️  Please run 'modal setup' first to configure your Modal account"
    exit 1
fi

# Deploy to Modal
echo "📦 Deploying to Modal..."
modal deploy main.py

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "📊 Check status: modal app list"
    echo "📝 View logs: modal app logs discord-poe-poc"
    echo "🛑 Stop app: modal app stop discord-poe-poc"
else
    echo "❌ Deployment failed!"
    exit 1
fi