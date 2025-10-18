# Discord-Poe-POC

A minimal Discord bot that integrates with the Poe API and deploys on Modal.

## Features

- 🤖 Discord bot with Poe AI integration
- ⚡ Fast deployment on Modal (~1.5s)
- 🔄 OpenAI-compatible API calls to Poe
- 🎯 Channel-specific responses
- 💬 Mention-based interactions

## Setup

### 1. Get API Keys

- **Discord Bot Token**: Visit [Discord Developer Portal](https://discord.com/developers/applications)
- **Poe API Key**: Get from [poe.com/api_key](https://poe.com/api_key)

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

### 3. Modal Deployment

Install Modal CLI:
```bash
pip install modal
modal setup
```

Deploy to Modal:
```bash
modal deploy main.py
```

### 4. Local Development

For local testing:
```bash
pip install -r requirements.txt
python main.py
```

## Configuration

### Allowed Models
Available Poe models include:
- `Claude-Sonnet-4`
- `Claude-Opus-4.1` 
- `GPT-4.1`
- `Gemini-2.5-Pro`
- `Llama-3.1-405B`
- `Grok-4`

### Channel Configuration
Update `ALLOWED_CHANNELS` in your environment or modify the `main.py` file directly.

## Commands

- `!ping` - Test bot responsiveness
- `!model [name]` - View/change AI model (planned feature)
- Direct messages or mentions trigger AI responses

## Modal Best Practices

- **Clean Deployments**: Use new app names for major changes
- **Secrets Management**: Store API keys in Modal secrets
- **Monitoring**: Check logs with `modal app logs discord-poe-poc`
- **Scaling**: Modal handles scaling automatically

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check channel IDs in configuration
2. **API errors**: Verify Poe API key and subscription status
3. **Deployment issues**: Ensure Modal CLI is properly set up

### Debug Commands

```bash
# Check Modal apps
modal app list

# View logs
modal app logs discord-poe-poc

# Stop app
modal app stop discord-poe-poc
```

## Architecture

- **main.py**: Core bot logic with Modal deployment
- **Modal Image**: Debian slim with Discord.py and OpenAI
- **Poe Integration**: OpenAI-compatible API calls
- **Discord Events**: Message handling and command processing

## Rate Limits

- Poe API: 500 requests per minute
- Discord: Standard bot rate limits apply
- Modal: No additional limits

## License

MIT License - see package.json for details