import discord
import database
import Techniques
from discord import app_commands
from discord.ext import commands
import TimeTracker

TECHNIQUES = {
    "pomodoro": Techniques.POMODORO,
    "90minblock": Techniques.NINETY_MIN_BLOCK,
    "freeflow": Techniques.FLOWTIME
}

class study(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_tracker = TimeTracker.TimeTracker()
        self.sessions = {}


    #DESCRIPTIONS FOR METHODS
    @app_commands.command(name="study_info", description="Informatio about each technique.")
    async def study_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Study Techniques",
            color=discord.Color.pink(),
        )
        embed.add_field(name="Pomodoro Method", value="Study for 25 minutes, break for 5 minutes, fourth break is 15 minutes.", inline=False)
        embed.add_field(name="90-Minute Block", value="Study for 90 minutes, break for 20 minutes.", inline=False)
        embed.add_field(name="Freeflow Method", value="Study however long you please!\n\n", inline=False)
        embed.set_footer(text="Use /start to begin a study session with your chosen technique.\n")
                         
        await interaction.response.send_message(embed=embed, ephemeral=True)


    #STOP TIMER
    @app_commands.command(name="study_stop", description="Stop your study timer.")
    @app_commands.guild_only()
    async def stop(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        session = self.sessions.pop(interaction.user.id, None)
        if session is None:
            await interaction.response.send_message("No timer to be stopped.")
            return
        session_min = await session.stop()
        await interaction.response.send_message(f"Timer stopped. Studied for {session_min} minutes.")

    #SELECT STUDY TECHNIQUES AND START TIMER
    @app_commands.command(name="study_start", description="Start your study timer.")
    @app_commands.describe(method="Choose your study technique")
    @app_commands.choices(method=[
        app_commands.Choice(name="Pomodoro", value="pomodoro"),
        app_commands.Choice(name="90-min Block", value="90minblock"),
        app_commands.Choice(name="Freeflow", value="freeflow"),
    ])
    @app_commands.guild_only()
    async def start(self, interaction: discord.Interaction, method: app_commands.Choice[str]):

        technique = TECHNIQUES[method.value]

        #STORE session into dictionary under user's ID
        session = techniques.StudySession(interaction.user, interaction.channel, technique, self.time_tracker)
        #RETRIEVE whatever is stored under this id
        self.sessions[interaction.user.id] = session
        session.start()

        await interaction.response.send_message(
            f"Started {technique.label}!"
        )

async def setup(bot):
    await bot.add_cog(study(bot))