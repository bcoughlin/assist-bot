"""
Discord-Poe-POC: A Discord bot integrated with Poe API, deployed on Modal
"""
import os
import asyncio
import modal
import discord
from openai import OpenAI
from discord.ext import commands
from config import Config, AVAILABLE_MODELS

# Modal app configuration
app = modal.App(Config.MODAL_APP_NAME)

# Modal image with required dependencies
image = modal.Image.debian_slim().pip_install([
    "discord.py==2.3.2",
    "openai==1.51.2",
    "python-dotenv==1.0.0"
])

# Modal secrets for environment variables
secrets = modal.Secret.from_dict({
    "DISCORD_TOKEN": os.environ.get("DISCORD_TOKEN", ""),
    "POE_API_KEY": os.environ.get("POE_API_KEY", ""),
    "DEFAULT_MODEL": os.environ.get("DEFAULT_MODEL", Config.DEFAULT_MODEL),
    "ALLOWED_CHANNELS": os.environ.get("ALLOWED_CHANNELS", ",".join(Config.ALLOWED_CHANNELS)),
    "SYSTEM_MESSAGE": os.environ.get("SYSTEM_MESSAGE", Config.SYSTEM_MESSAGE),
})

@app.function(
    image=image,
    secrets=[secrets],
    keep_warm=Config.KEEP_WARM,
    timeout=Config.TIMEOUT,
)
def run_discord_bot():
    """Main function to run the Discord bot"""
    
    # Validate configuration
    config_errors = Config.validate()
    if config_errors:
        for error in config_errors:
            print(f"❌ Configuration Error: {error}")
        return
    
    # Initialize Poe API client (OpenAI-compatible)
    poe_client = OpenAI(
        api_key=os.environ["POE_API_KEY"],
        base_url=Config.POE_BASE_URL
    )
    
    # Discord bot configuration
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guild_messages = True
    
    bot = commands.Bot(command_prefix=Config.COMMAND_PREFIX, intents=intents)
    
    # Load configuration from environment
    allowed_channels = os.environ.get("ALLOWED_CHANNELS", ",".join(Config.ALLOWED_CHANNELS)).split(",")
    current_model = os.environ.get("DEFAULT_MODEL", Config.DEFAULT_MODEL)
    system_message = os.environ.get("SYSTEM_MESSAGE", Config.SYSTEM_MESSAGE)
    
    @bot.event
    async def on_ready():
        print(f'🤖 {bot.user} has connected to Discord!')
        print(f'📊 Bot is in {len(bot.guilds)} guilds')
        print(f'🧠 Using model: {current_model}')
        print(f'📍 Allowed channels: {allowed_channels}')
    
    @bot.event
    async def on_message(message):
        # Don't respond to bot messages
        if message.author.bot:
            return
        
        # Ignore messages with certain prefixes
        if any(message.content.startswith(prefix) for prefix in Config.IGNORE_PREFIXES):
            return
        
        # Only respond in allowed channels or when mentioned
        is_allowed_channel = str(message.channel.id) in allowed_channels
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
    
    @bot.command(name='help')
    async def help_command(ctx):
        """Show help information"""
        help_text = """
🤖 **Discord-Poe-POC Bot Commands**

**Basic Commands:**
• `!ping` - Test bot responsiveness
• `!model` - Show current AI model
• `!models` - List available models
• `!help` - Show this help message

**AI Interaction:**
• Mention the bot or message in allowed channels for AI responses
• Uses Poe API with multiple model options

**Configured Channels:** {channels}
**Current Model:** `{model}`
        """.format(
            channels=", ".join([f"<#{ch}>" for ch in allowed_channels]),
            model=current_model
        )
        await ctx.send(help_text)
    
    # Run the bot
    bot.run(os.environ["DISCORD_TOKEN"])

# Modal deployment entry point
@app.local_entrypoint()
def main():
    """Entry point for Modal deployment"""
    run_discord_bot.remote()

if __name__ == "__main__":
    # For local development
    import dotenv
    dotenv.load_dotenv()
    run_discord_bot()