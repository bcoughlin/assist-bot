#!/bin/bash

# Discord-Poe-POC Local Development Script

echo "🔧 Setting up local development environment..."

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before running the bot"
    echo "   - DISCORD_TOKEN: Get from https://discord.com/developers/applications"
    echo "   - POE_API_KEY: Get from https://poe.com/api_key"
    exit 1
fi

echo "✅ Development environment ready!"
echo "🚀 Run the bot locally: python main.py"
echo "☁️  Deploy to Modal: ./deploy.sh"