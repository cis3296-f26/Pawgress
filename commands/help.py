import discord
from discord import app_commands
from discord.ext import commands
from pet import Pet

class help(commands.Cog):

    def __init__(self, bot):    
        self.bot = bot

    #HELP
    @app_commands.command(name="help", description="List commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "/help - List commands\n"
            "/create_pet - Create a new pet\n"
            "/rename_pet - Rename your pet\n"
            "/study_info - Display study method descriptions\n"
            "/start - Select and start a study session\n"
            "/stop - End a study session\n"
            "/catalog - Display food tiers\n"
            "/buy - Select and buy food\n"
            ,ephemeral=False)

    ''' Evan's secret feature?
    @app_commands.command(name="walter", description="Make it end")
    @app_commands.guild_only()
    async def walter(self, interaction: discord.Interaction):
        await interaction.response.send_message("Walter.")
    '''

async def setup(bot):
    await bot.add_cog(help(bot))