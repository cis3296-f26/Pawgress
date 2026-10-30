import discord
import database
from discord import app_commands
from discord.ext import commands
import TimeTracker
from views.SelectView import SelectView

class study(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_tracker = TimeTracker.TimeTracker()

        self.study_techniques = {
            "pomodoro": self.start_pomodoro,
            "90minblock": self.start_90minblock,
            "freeflow": self.start_freeflow,
        }

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
            await interaction.response.send_message("Timer Stopped. Total Time: " + message)
        else:
            await interaction.response.send_message("No timer to be stopped :(")

    #SELECT STUDY TECHNIQUES AND START TIMER
    @app_commands.command(name="start", description="Start your study timer")
    @app_commands.guild_only()
    async def start(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return
        
        #Call the selection view for ui
        view = SelectView(interaction.user)
        await interaction.response.send_message("Please select your study method:", view=view)
        await view.wait()

        if view.choice is None:
            await interaction.edit_original_response(content="Timed out: please retry.", view=None)
            return

        #Call whichever function needed for the selected method
        await self.study_techniques[view.choice](interaction)

    
    #POMODORO TECHNIQUE (to do)
    async def start_pomodoro(self, interaction):
        await interaction.followup.send("To be implemented")


    #90 MIN BLOCK TECHNIQUE (to do)
    async def start_90minblock(self, interaction: discord.Interaction):
        await interaction.followup.send("To be implemented")


    #FREEFLOW (to do)
    async def start_freeflow(self, interaction):
        await interaction.followup.send("To be implemented")


async def setup(bot):
    await bot.add_cog(study(bot))