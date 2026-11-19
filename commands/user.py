import discord
import database
from discord import app_commands
from discord.ext import commands

print(database.__file__)
print(dir(database))

#1: regular, 2: super, 3: mega
COSTS = {1: 15, 2: 20, 3: 45} 


class User(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user_balance", description="Check how many coins you have")
    @app_commands.guild_only()
    async def check_balance(self, interaction: discord.Interaction):
        coins = await database.get_coins(interaction.user.id)
        await interaction.response.send_message(
            f"You have **{coins}** coins", ephemeral=True
        )

    
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


    #CHECK INVENTORY
    @app_commands.command(name="user_inventory", description="Check your inventory")
    @app_commands.guild_only()
    async def check_inventory(self, interaction: discord.Interaction):

        user_id = await database.get_or_create_user(interaction.user.id, interaction.user.name)
        inventory = await database.get_inventory(user_id)

        if not inventory:
            await interaction.response.send_message(
                f"{interaction.user.display_name} has no items in their inventory.", ephemeral=True
            )
            return

        embed = discord.Embed(title=f"{interaction.user.display_name}'s Inventory:")

        for item_name, quantity, hunger_value in inventory:
            embed.add_field(
                name=item_name,
                value=f"Quantity: **{quantity}**",
                inline=True,
            )

        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(User(bot))