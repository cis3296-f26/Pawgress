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
        embed = discord.Embed(
            title="Pawgress Commands",
            description="Study to earn coins, then spend them on food for your pet!",
            color=discord.Color.pink(),
        )

        embed.add_field(
            name="General",
            value="/help - List commands",
            inline=False,
        )
        embed.add_field(
            name="Pet",
            value=(
                "/pet_rename - Rename your pet\n"
                "/pet_change - Change your pet type"
            ),
            inline=False,
        )
        embed.add_field(
            name="Study",
            value=(
                "/study_info - Display study method descriptions\n"
                "/study_start - Select and start a study session\n"
                "/study_stop - End a study session"
            ),
            inline=False,
        )
        embed.add_field(
            name="Store",
            value=(
                "/store_catalog - Display food items and prices\n"
                "/store_buy - Select and buy food"
            ),
            inline=False,
        )
        embed.add_field(
            name="User",
            value=(
                "/user_balance - Check how many coins you have\n"
                "/user_inventory - Check your inventory to see items you have purchased"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

    ''' Evan's secret feature?
    @app_commands.command(name="walter", description="Make it end")
    @app_commands.guild_only()
    async def walter(self, interaction: discord.Interaction):
        await interaction.response.send_message("Walter.")
    '''

async def setup(bot):
    await bot.add_cog(help(bot))