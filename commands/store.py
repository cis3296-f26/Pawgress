import discord
import database
from discord import app_commands
from discord.ext import commands

print(database.__file__)
print(dir(database))
class Store(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #STORE CATALOG
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

    #STORE BUY
    @app_commands.command(name="buy", description="Select and buy food")
    @app_commands.describe(food="Choose your food item:")
    @app_commands.choices(food=[
        app_commands.Choice(name = "Regular Food", value = "regularfood"),
        app_commands.Choice(name = "Super Food", value = "superfood"),
        app_commands.Choice(name = "Mega Food", value = "megafood")
    ])
    @app_commands.guild_only()
    async def store_buy(self, interaction: discord.Interaction, food: app_commands.Choice[str]):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        #Food that was selected
        if food.value == "regularfood":
            hunger = 15
            cost = 15
        elif food.value == "superfood":
            hunger = 25
            cost = 20
        elif food.value == "megafood":
            hunger = 50
            cost = 45

        #Charge the user and update the pet's hunger (NEEDS WORK)
        await interaction.response.send_message(
            f"You bought **{food.name}** for {cost} coins! (+{hunger} hunger)"
        )


async def setup(bot):
    await bot.add_cog(Store(bot))