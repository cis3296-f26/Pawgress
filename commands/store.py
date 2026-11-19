import discord
import database
from discord import app_commands
from discord.ext import commands

print(database.__file__)
print(dir(database))

#1: regular, 2: super, 3: mega
COSTS = {1: 15, 2: 20, 3: 45} 


class Store(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #STORE CATALOG
    @app_commands.command(name="store_catalog", description="Opens a list of items that are avilable for purchase")
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


    #STORE BUY
    @app_commands.command(name="store_buy", description="Select and buy food")
    @app_commands.describe(food="Choose your food item:")
    @app_commands.choices(food=[
        app_commands.Choice(name = "Regular Food", value = 1),
        app_commands.Choice(name = "Super Food", value = 2),
        app_commands.Choice(name = "Mega Food", value = 3)
    ])
    @app_commands.guild_only()
    async def store_buy(self, interaction: discord.Interaction, food: app_commands.Choice[int]):

        cost = COSTS[food.value]

        new_balance = await database.purchase_item(
            interaction.user.id,interaction.user.name,food.value,cost
        )

        if new_balance is None:
            await interaction.response.send_message(
                f"You don't have enough coins for {food.name}", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{interaction.user.display_name} bought **{food.name}** for {cost} coins!"
        )

async def setup(bot):
    await bot.add_cog(Store(bot))