import discord
import database
import techniques
from discord import app_commands
from discord.ext import commands
import TimeTracker
from views.SelectView import SelectView

class study(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_tracker = TimeTracker.TimeTracker()
        self.sessions = {}

        self.study_techniques = {
            "pomodoro": self.start_pomodoro,
            "90minblock": self.start_90minblock,
            "freeflow": self.start_freeflow,
        }

    #STOP TIMER
    @app_commands.command(name="stop", description="Stop your study timer.")
    @app_commands.guild_only()
    async def stop(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        session = self.sessions.pop(interaction.user.id, None)
        if session is None:
            await interaction.response.send_message("No timer to be stopped.")
            return
        session_min = session.stop()
        await interaction.response.send_message(f"Timer stopped. Studied for {session_min} minutes.")

    #SELECT STUDY TECHNIQUES AND START TIMER
    @app_commands.command(name="start", description="Start your study timer.")
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

    async def begin(self, interaction: discord.Interaction, technique):
        if interaction.user.id in self.sessions:
            await interaction.followup.send("Already Studying!")
            return

        session = techniques.StudySession(interaction.user, interaction.channel, technique, self.time_tracker)
        self.sessions[interaction.user.id] = session
        session.start()

        await interaction.followup.send(f"Started {technique.label}: {technique.description}")

    async def start_pomodoro(self, interaction):
        await self.begin(interaction, techniques.POMODORO)

    async def start_90minblock(self, interaction: discord.Interaction):
        await self.begin(interaction, techniques.NINETY_MIN_BLOCK)

    async def start_freeflow(self, interaction):
        await self.begin(interaction, techniques.FLOWTIME)


async def setup(bot):
    await bot.add_cog(study(bot))