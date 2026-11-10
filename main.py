import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pathlib import Path
import createTables
import database

env_path = Path(__file__).parent / ".env"
print("Looking for:", env_path, "| exists:", env_path.exists())
print("Loaded:", load_dotenv(env_path, override=True))

token = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("DISCORD_TOKEN not found. Check your .env file.")

intents = discord.Intents.default()

intents.message_content = True

DEFAULT_PET_NAME = "Pawgress"
DEFAULT_PET_TYPE = "Dog"

class PawgressBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        #Create tables first
        await createTables.init_db()   

        #Load command files
        await self.load_extension("commands.help")
        await self.load_extension("commands.pet")
        await self.load_extension("commands.study")
        await self.load_extension("commands.store")
        await self.load_extension("commands.user")

        #Tells discord which commands are available for the bot to use
        await self.tree.sync()   

    async def on_ready(self):
        print(f"Logged in as {self.user}")



    #PET CREATE: This event is triggered when the bot joins a new guild (server)

    async def on_guild_join(self, guild):

        #Create a default pet for the guild if it doesn't exist (skip if server already had one like they re-added it)
        if not await database.get_pet(guild.id):
            await database.create_pet(guild.id, DEFAULT_PET_NAME, DEFAULT_PET_TYPE)

        #Find a channel the bot can send messages in (certain permissions may be required?)
        channel = guild.system_channel
        if channel is None or not channel.permissions_for(guild.me).send_messages:
            channel = next(
                (channel for channel in guild.text_channels
                if channel.permissions_for(guild.me).send_messages),
                None
            )

        if channel is not None:
            await channel.send(
                f"Hello! I'm **{DEFAULT_PET_NAME}** the **{DEFAULT_PET_TYPE}**, your new study companion! 🐾\n"
                f"Use `/pet_rename` and `/pet_change` to make me your own, or `/help` to see everything I can do."
            )


bot = PawgressBot()
bot.run(token)