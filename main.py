"""
Discord-Poe-POC: A Discord bot integrated with Poe API, deployed on Modal
"""
import os
import modal

# Import config at module level for Modal
try:
    from config import Config, AVAILABLE_MODELS
except ImportError:
    # Fallback config for Modal environment
    class Config:
        MODAL_APP_NAME = "discord-poe-poc"
        POE_BASE_URL = "https://api.poe.com/v1"
        DEFAULT_MODEL = "LastzAiBeta"  # Your custom Poe bot
        COMMAND_PREFIX = "!"
        IGNORE_PREFIXES = ["!", "?", "/"]
        ALLOWED_CHANNELS = ["663843965325410319"]
        MAX_RESPONSE_LENGTH = 2000
        MAX_TOKENS = 1000
        TEMPERATURE = 0.7
        SYSTEM_MESSAGE = "You are a helpful Discord bot assistant. Be concise and friendly."
        KEEP_WARM = 1
        TIMEOUT = 3600
        
        @classmethod
        def validate(cls):
            errors = []
            if not os.environ.get("DISCORD_TOKEN"):
                errors.append("DISCORD_TOKEN is required")
            if not os.environ.get("POE_API_KEY"):
                errors.append("POE_API_KEY is required")
            return errors
    
    AVAILABLE_MODELS = [
        "LastzAiBeta", "Claude-Sonnet-4", "Claude-Opus-4.1", "GPT-4.1", 
        "Gemini-2.5-Pro", "Llama-3.1-405B", "Grok-4"
    ]

# Modal app configuration
app = modal.App(Config.MODAL_APP_NAME)

# Modal image with required dependencies
image = (
    modal.Image.debian_slim()
    .apt_install("python3-dev", "build-essential")
    .pip_install([
        "discord.py==2.4.0",  # Updated version with Python 3.13 support
        "openai==1.40.0",  # Older version to avoid proxies argument issue
        "httpx<0.28.0",  # Pin httpx to avoid proxies argument issue
        "python-dotenv==1.0.0"
    ])
)

# Use Modal secret with Discord and Poe API keys (updated with correct Poe key)
secrets = [modal.Secret.from_name("discord-secrets-v2")]

@app.function(
    image=image,
    secrets=secrets,
    min_containers=1,
    timeout=Config.TIMEOUT,
)
def run_discord_bot():
    """Main function to run the Discord bot"""
    
    # Patch missing audioop module for Python 3.13 compatibility
    import sys
    if 'audioop' not in sys.modules:
        import types
        sys.modules['audioop'] = types.ModuleType('audioop')
        sys.modules['audioop'].error = Exception
    
    # Import Discord modules inside the function for Modal
    import discord
    from openai import OpenAI
    from discord.ext import commands
    
    # Validate configuration
    config_errors = Config.validate()
    if config_errors:
        for error in config_errors:
            print(f"❌ Configuration Error: {error}")
        return
    
    # Initialize Poe API client (OpenAI-compatible)
    try:
        poe_client = OpenAI(
            api_key=os.environ["POE_API_KEY"],
            base_url=Config.POE_BASE_URL
        )
        print("✅ Poe API client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Poe API client: {e}")
        raise
    
    # Discord bot configuration
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guild_messages = True
    
    # Disable voice support to avoid audioop dependency issues
    bot = commands.Bot(
        command_prefix=Config.COMMAND_PREFIX, 
        intents=intents,
        enable_debug_events=False
    )
    
    # Load configuration from environment
    allowed_channels_str = os.environ.get("ALLOWED_CHANNELS", ",".join(Config.ALLOWED_CHANNELS))
    allowed_channels = [ch.strip() for ch in allowed_channels_str.split(",") if ch.strip()]
    current_model = os.environ.get("DEFAULT_MODEL", "LastzAiBeta")  # Use your custom Poe bot
    system_message = os.environ.get("SYSTEM_MESSAGE", Config.SYSTEM_MESSAGE)
    
    @bot.event
    async def on_ready():
        print(f'🤖 {bot.user} has connected to Discord!')
        print(f'📊 Bot is in {len(bot.guilds)} guilds')
        print(f'🧠 Using model: {current_model}')
        if allowed_channels:
            print(f'📍 Allowed channels: {allowed_channels}')
        else:
            print('📍 Responding in all channels')
        
        # Set bot status
        activity = discord.Activity(type=discord.ActivityType.listening, name="for mentions and commands")
        await bot.change_presence(status=discord.Status.online, activity=activity)
    
    @bot.event
    async def on_message(message):
        # Don't respond to bot messages
        if message.author.bot:
            return
        
        # Ignore messages with certain prefixes
        if any(message.content.startswith(prefix) for prefix in Config.IGNORE_PREFIXES):
            return
        
        # Only respond in allowed channels or when mentioned
        # If no channels specified, respond everywhere
        is_allowed_channel = len(allowed_channels) == 0 or str(message.channel.id) in allowed_channels
        is_mentioned = bot.user in message.mentions
        
        if not (is_allowed_channel or is_mentioned):
            return
        
        # Show typing indicator
        async with message.channel.typing():
            try:
                # Call Poe API
                response = poe_client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": message.content
                        }
                    ],
                    max_tokens=Config.MAX_TOKENS,
                    temperature=Config.TEMPERATURE
                )
                
                reply_content = response.choices[0].message.content
                
                # Discord has a 2000 character limit for messages
                if len(reply_content) > Config.MAX_RESPONSE_LENGTH:
                    reply_content = reply_content[:Config.MAX_RESPONSE_LENGTH-3] + "..."
                
                await message.reply(reply_content)
                
            except Exception as e:
                print(f"❌ Error calling Poe API: {e}")
                print(f"❌ Error type: {type(e).__name__}")
                print(f"❌ Message content: {message.content}")
                await message.reply("Sorry, I encountered an error processing your request.")
        
        # Process commands
        await bot.process_commands(message)
    
    @bot.command(name='ping')
    async def ping(ctx):
        """Simple ping command"""
        latency = round(bot.latency * 1000)
        await ctx.send(f'🏓 Pong! Latency: {latency}ms')
    
    @bot.command(name='model')
    async def show_model(ctx):
        """Show current AI model"""
        await ctx.send(f'🧠 Current model: `{current_model}`')
    
    @bot.command(name='models')
    async def list_models(ctx):
        """List available AI models"""
        models_text = "🤖 Available models:\n" + "\n".join([f"• `{model}`" for model in AVAILABLE_MODELS[:10]])
        if len(AVAILABLE_MODELS) > 10:
            models_text += f"\n... and {len(AVAILABLE_MODELS) - 10} more"
        await ctx.send(models_text)
    
    @bot.command(name='bothelp')
    async def bot_help_command(ctx):
        """Show bot help information"""
        help_text = """
🤖 **Discord-Poe-POC Bot Commands**

**Basic Commands:**
• `!ping` - Test bot responsiveness
• `!model` - Show current AI model
• `!models` - List available models
• `!bothelp` - Show this help message

**AI Interaction:**
• Mention the bot or message in allowed channels for AI responses
• Uses Poe API with multiple model options

**Configured Channels:** {channels}
**Current Model:** `{model}`
        """.format(
            channels=", ".join([f"<#{ch}>" for ch in allowed_channels]) if allowed_channels else "All channels",
            model=current_model
        )
        await ctx.send(help_text)
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        print(f"❌ Discord error in {event}: {args}")
    
    # Run the bot with error handling
    try:
        bot.run(os.environ["DISCORD_TOKEN"])
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        raise

# Modal deployment entry point
@app.local_entrypoint()
def main():
    """Entry point for Modal deployment"""
    keep_bot_alive.remote()

# Keep-alive function to maintain the bot running
@app.function(
    image=image,
    secrets=secrets,
    timeout=3600 * 24,  # 24 hour timeout
    min_containers=1,  # Keep one instance running
)
def keep_bot_alive():
    """Keep the bot running continuously"""
    print("🚀 Starting Discord bot...")
    
    # Call the bot function locally within the same container
    run_discord_bot.local()
    print("⚠️ Bot stopped unexpectedly")

if __name__ == "__main__":
    # For local development
    try:
        import dotenv
        import discord
        from openai import OpenAI
        from discord.ext import commands
        dotenv.load_dotenv()
        run_discord_bot()
    except ImportError as e:
        print(f"❌ Missing dependencies for local development: {e}")
        print("🔧 Run: pip install -r requirements.txt")