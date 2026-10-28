import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pathlib import Path
import createTables


env_path = Path(__file__).parent / ".env"
print("Looking for:", env_path, "| exists:", env_path.exists())
print("Loaded:", load_dotenv(env_path, override=True))

token = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("DISCORD_TOKEN not found. Check your .env file.")

intents = discord.Intents.default()

intents.message_content = True

class PawgressBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await createTables.init_db()    # create tables first
        await self.load_extension("commands.petcmds")
        await self.tree.sync()   # Tells discord which commands are available for the bot to use

    async def on_ready(self):
        print(f"Logged in as {self.user}")


""" Up for discussion:
@client.event # This event is triggered when the bot joins a new guild (server)
async def on_guild_join(guild):
    # Create a new text channel for the bot? This can be up for discussion
    channel = await guild.create_text_channel("pawgress-channel")

    await channel.send("Hello! I'm Pawgress, your furry study bot.")"""


bot = PawgressBot()
bot.run(token)