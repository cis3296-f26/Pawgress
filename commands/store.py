import discord
import database
from discord import app_commands
from discord.ext import commands

print(database.__file__)
print(dir(database))
class Store(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Store
    
    @app_commands.command(name="catalog", description="Opens a list of items that are avilable for purchase")
    @app_commands.guild_only()
    async def store_catalog(self, interaction: discord.Interaction):
        items = await database.get_store_catalog()
        if not items:
            await interaction.response.send_message(
                "The store is empty right now.", ephemeral=True
            )
            return
        embed = discord.Embed(
            title="Store Catalog",
            description="Items you can buy for your pet:",
        )

        for item in items:
            embed.add_field(
                name=item["item_name"],
                value=f"Hunger restored: **{item['item_hunger_value']}**\n"
                      f"Cost: **{item['item_cost']}** coins",
                inline=True,
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Store(bot))