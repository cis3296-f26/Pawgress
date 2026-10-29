import discord
import database
from discord import app_commands
from discord.ext import commands
import TimeTracker

class study(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_tracker = TimeTracker.TimeTracker()

    #STOP TIMER
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

    #START TIMER
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
    
   
async def setup(bot):
    await bot.add_cog(study(bot))