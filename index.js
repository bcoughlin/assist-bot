import { config } from 'dotenv'; config()
import { Client } from 'discord.js';
import { OpenAI } from 'openai';
import { createBackendClient } from '@pipedream/sdk/server';
 
// Initialize the Pipedream SDK client
const pd = createBackendClient({
  environment: process.env.PIPEDREAM_ENVIRONMENT,
  credentials: {
    clientId: process.env.PIPEDREAM_CLIENT_ID,
    clientSecret: process.env.PIPEDREAM_CLIENT_SECRET,
  },
  projectId: process.env.PIPEDREAM_PROJECT_ID
});
 
// Find the app to use for the MCP server
const apps = await pd.getApps({ q: "discord" });
const appSlug = 'google_docs';
 
// Get access token for MCP server auth
const accessToken = await pd.rawAccessToken();
 
// Send the unique ID that you use to identify this user in your system
const externalUserId = 'brad-test'; // Used in MCP URL to identify the user

const client = new Client({
    intents: ['Guilds', 'GuildMembers', 'GuildMessages', 'MessageContent'],
});

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

// Define the prefixes to ignore and the channels to respond in
const IGNORE_PREFIXES = ['!', '?'];
const CHANNELS = ['663843965325410319'];

const openai = new OpenAI({
    apiKey: process.env.OPENAI_KEY,
});

const responseArray = [];

client.on('messageCreate', async (message) => {
    // Don't respond to messages from bots
    if (message.author.bot) return;

    // Ignore messages that start with certain prefixes
    if (IGNORE_PREFIXES.some(prefix => message.content.startsWith(prefix))) return;
    
    // Only respond if in specific channels or if mentioned
    if (!CHANNELS.includes(message.channel.id) && !message.mentions.users.has(client.user.id)) return;
    
    console.log('message.mentions.users: ' + message.mentions.users.map(user => user.id));
    console.log('User ID: ' + client.user.id);
    console.log('Content: ' + message.content);

    const response = await openai.responses.create({
        prompt: {
            "id": "pmpt_6876d1b03edc8193ad6b5684bae0af8d0820aa045d9844f4",
            "version": "7"
        },
        previous_response_id: responseArray.length > 0 ? responseArray[responseArray.length - 1].id : undefined,
        model: 'gpt-4o-mini',
        tools: [
            {
            type: 'mcp',
            server_label: appSlug,
            server_url: `https://remote.mcp.pipedream.net`,
            headers: {
                Authorization: `Bearer ${accessToken}`,
                "x-pd-project-id": process.env.PIPEDREAM_PROJECT_ID,
                "x-pd-environment": process.env.PIPEDREAM_ENVIRONMENT,
                "x-pd-external-user-id": externalUserId,
                "x-pd-app-slug": appSlug,
            },
            require_approval: 'never'
            }
        ],
        input: message.content,
        store: true,
    })
    .catch((error) => console.error('Error from OpenAI:', error));

    message.reply(response.output_text);

    // add the response to the array
    responseArray.push({
        id: response.id,
    });
});

client.login(process.env.TOKEN)