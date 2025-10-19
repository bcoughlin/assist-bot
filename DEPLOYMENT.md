# Discord-Poe Bot Deployment Guide

## Current Deployment Status

Your Discord bot is currently running using a **two-step deployment process** that's admittedly confusing. Let me explain what's actually happening:

## How It's Currently Working

### Step 1: Deploy Functions to Modal
```bash
./deploy.sh
```
This deploys the Modal app and creates the functions, but **doesn't start the bot**. You'll see:
- ✅ App deployed successfully  
- ✅ Functions created (`run_discord_bot`, `keep_bot_alive`)
- ❌ Bot still offline (only 2 tasks running instead of 3)

### Step 2: Start the Bot Manually
```bash
nohup modal run main.py::main > bot.log 2>&1 &
```
This actually starts the Discord bot by calling the `main()` function in the background:
- ✅ Bot connects to Discord
- ✅ Shows as "LastZAiBeta#4976" online
- ✅ Uses your custom LastzAiBeta model
- ✅ Creates an "ephemeral" Modal app instance

## Why This Two-Step Process?

The issue is in the Modal app design:

1. **The `main()` function** calls `keep_bot_alive.remote()` to start the bot
2. **Modal deployment** only creates the functions but doesn't call `main()`
3. **Manual execution** of `main()` is needed to actually start the Discord connection

## Current Status Check

### Check if Bot is Running
```bash
# Check Modal apps
modal app list | grep discord-poe-poc

# Check local background process
ps aux | grep modal

# Check bot logs
cat bot.log
```

### Bot Information
- **Bot Name**: LastZAiBeta#4976
- **Model**: LastzAiBeta (your custom Poe model)
- **Allowed Channel ID**: 663843965325410319
- **Log File**: `bot.log`

## Managing the Bot

### Stop the Bot
```bash
# Find the process ID
ps aux | grep "modal run main.py::main"

# Kill the process (replace XXXX with actual PID)
kill XXXX

# Or stop all Modal apps
modal app stop discord-poe-poc
```

### Restart the Bot
```bash
# Stop any existing instances
pkill -f "modal run main.py::main"

# Deploy fresh functions
./deploy.sh

# Start the bot
nohup modal run main.py::main > bot.log 2>&1 &
```

### Monitor the Bot
```bash
# Watch logs in real-time
tail -f bot.log

# Check latest logs
cat bot.log | tail -20

# Check Modal app status
modal app list
```

## Better Deployment Strategy (Future Improvement)

The current setup works but isn't ideal. A better approach would be:

### Option 1: Auto-Start Function
Modify the Modal app to automatically call `main()` on deployment:

```python
@app.function()
def startup():
    """Auto-start function called on deployment"""
    main()

if __name__ == "__main__":
    # Auto-start when deployed
    startup.remote()
```

### Option 2: Scheduled Function
Use Modal's scheduling to keep the bot running:

```python
@app.function(schedule=modal.Cron("*/5 * * * *"))  # Check every 5 minutes
def keep_bot_running():
    # Check if bot is running, restart if needed
    pass
```

### Option 3: Web Endpoint
Create a web endpoint to start/stop the bot remotely:

```python
@app.function()
@web_endpoint(method="POST")
def start_bot():
    main()
    return {"status": "Bot started"}
```

## Troubleshooting

### Bot Shows Offline
1. Check if the background process is running: `ps aux | grep modal`
2. Check the logs: `cat bot.log`
3. Restart: `pkill -f "modal run" && nohup modal run main.py::main > bot.log 2>&1 &`

### Bot Not Responding
1. Check Discord permissions (privileged intents enabled?)
2. Check Poe API key in Modal secrets
3. Verify channel permissions

### Modal Errors
1. Check secrets: `modal secret list`
2. Update secrets if needed: `modal secret create discord-secrets-v2`
3. Redeploy: `./deploy.sh`

## Summary

**Current Working Setup:**
1. `./deploy.sh` - Deploys functions to Modal
2. `nohup modal run main.py::main > bot.log 2>&1 &` - Starts the bot
3. Bot runs as "LastZAiBeta#4976" using your LastzAiBeta model
4. Monitor with `cat bot.log` and `modal app list`

This setup works but could be simplified in the future with auto-start functionality.