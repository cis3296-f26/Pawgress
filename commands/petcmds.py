import discord
import database
from discord import app_commands
from discord.ext import commands
from pet import Pet
import TimeTracker

print(database.__file__)
print(dir(database))
class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_tracker = TimeTracker.TimeTracker()

    # Commands here. We can add more commands like name, feed, etc.

    #pet creation command
    @app_commands.command(name="create_pet", description="Create a new pet for this server")
    @app_commands.guild_only()
    async def create_pet(self, interaction: discord.Interaction):
        if await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("This server already has a pet!")
            return
        
        await database.create_pet(
            # placeholders
            interaction.guild_id, name="No name", pet_type="Dog"
        )
        await interaction.response.send_message("Your new pet has been created!")

    #rename pet command
    @app_commands.command(name="rename_pet", description="Rename your server's pet")
    @app_commands.guild_only()
    async def rename_pet(self, interaction: discord.Interaction, name: str):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.rename_pet(interaction.guild_id, name)
        await interaction.response.send_message(f"Your pet is now named **{name}**!")

    #stop timer
    @app_commands.command(name="stop", description="Stop your study timer")
    @app_commands.guild_only()
    async def stop(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        result = self.time_tracker.timer_stop(interaction.user.id)
        message = self.time_tracker.get_time(interaction.user.id)
        if result == 0:
            await interaction.response.send_message("Timer Stopped, Time: " + message)
        else:
            await interaction.response.send_message("No timer to be stopped :(")

    #start timer
    @app_commands.command(name="start", description="Stop your study timer")
    @app_commands.guild_only()
    async def start(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        result = self.time_tracker.timer_start(interaction.user.id)
        if result == 0:
            await interaction.response.send_message("Timer Started")
        else:
            await interaction.response.send_message("Timer already started :(")


    @app_commands.command(name="walter", description="Make it end")
    @app_commands.guild_only()
    async def walter(self, interaction: discord.Interaction):
        await interaction.response.send_message("Walter.")

    #help command
    @app_commands.command(name="help", description="list commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("/help - list commands\n/create_pet - create a new pet\n/rename_pet - rename your pet", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Pets(bot))