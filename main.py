import discord
from discord.ext import commands
from datetime import datetime
import os
from dotenv import load_dotenv

print("script started")
class Client(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.active_sessions = {}

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print('------')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        #check if the message starts with a specific command(!hello)
        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')
            
    async def on_voice_state_update(self, member, before, after):
        # Case 1: User joined a Voice Chat (was not in one before, but is in one now)
        if before.channel is None and after.channel is not None:
            self.active_sessions[member.id] = datetime.now()
            print(f"[JOIN] {member.name} joined {after.channel.name} at {self.active_sessions[member.id]}")

        # Case 2: User left a Voice Chat (was in one before, but is not in one now)
        elif before.channel is not None and after.channel is None:
            join_time = self.active_sessions.pop(member.id, None)
            
            if join_time:
                leave_time = datetime.now()
                duration = leave_time - join_time
                
                # Extract hours, minutes, and seconds from total duration
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"[LEAVE] {member.name} left {before.channel.name}.")
                print(f"Session Duration: {hours}h {minutes}m {seconds}s")

        # Case 3: User switched Voice Chats (was in one before, and is in a different one now)
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            join_time = self.active_sessions.get(member.id)
            leave_time = datetime.now()
        
            if join_time:
                duration = leave_time - join_time
                print(f"[SWITCH] {member.name} moved from {before.channel.name} to {after.channel.name}.")
                print(f"Time spent in previous channel: {duration}")
            self.active_sessions[member.id] = datetime.now()

intents = discord.Intents.default()
intents.message_content = True

# Load environment variables from .env file
from pathlib import Path

env_path = Path(__file__).parent / ".env"
print("Looking for:", env_path, "| exists:", env_path.exists())
print("Loaded:", load_dotenv(env_path, override=True))

token = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("DISCORD_TOKEN not found. Check your .env file.")

client = Client(intents=intents)
client.run(token)