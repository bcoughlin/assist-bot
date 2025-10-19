#!/bin/bash

# Discord Bot Management Script

case "$1" in
    "status")
        echo "🤖 Checking Discord Bot Status..."
        echo ""
        echo "📊 Modal Apps:"
        modal app list | grep discord-poe-poc
        echo ""
        echo "💻 Local Processes:"
        ps aux | grep "modal run main.py::main" | grep -v grep
        echo ""
        echo "📝 Recent Logs:"
        if [ -f "bot.log" ]; then
            tail -5 bot.log
        else
            echo "No bot.log file found"
        fi
        ;;
    "start")
        echo "🚀 Starting Discord Bot..."
        # Stop any existing instances first
        pkill -f "modal run main.py::main" 2>/dev/null
        # Deploy functions
        ./deploy.sh
        # Start bot in background
        nohup modal run main.py::main > bot.log 2>&1 &
        echo "✅ Bot started! Check status with: ./bot.sh status"
        ;;
    "stop")
        echo "🛑 Stopping Discord Bot..."
        pkill -f "modal run main.py::main"
        modal app stop discord-poe-poc 2>/dev/null
        echo "✅ Bot stopped"
        ;;
    "restart")
        echo "🔄 Restarting Discord Bot..."
        $0 stop
        sleep 2
        $0 start
        ;;
    "logs")
        echo "📝 Bot Logs:"
        if [ -f "bot.log" ]; then
            tail -f bot.log
        else
            echo "No bot.log file found"
        fi
        ;;
    *)
        echo "🤖 Discord Bot Management"
        echo ""
        echo "Usage: $0 {status|start|stop|restart|logs}"
        echo ""
        echo "Commands:"
        echo "  status   - Check if bot is running"
        echo "  start    - Deploy and start the bot"
        echo "  stop     - Stop the bot"
        echo "  restart  - Stop and start the bot"
        echo "  logs     - Show bot logs (live)"
        echo ""
        echo "Current Bot: LastZAiBeta#4976"
        echo "Model: LastzAiBeta (Custom Poe Model)"
        ;;
esac