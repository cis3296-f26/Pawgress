import discord
import database
from discord import app_commands
from discord.ext import commands
from pet import Pet

print(database.__file__)
print(dir(database))
class Pets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #CREATE PET
    @app_commands.command(name="pet_create", description="Create a new pet for this server")
    @app_commands.guild_only()
    async def create_pet(self, interaction: discord.Interaction):
        existing = await database.get_pet(interaction.guild_id)
        if existing:
            _, pet_name, pet_type, _ = existing
            await interaction.response.send_message(f"This server already has a pet: **{pet_name}** the **{pet_type}**")
            return

        await database.create_pet(
            # placeholders
            interaction.guild_id, name="No name", pet_type="Dog"
        )
        await interaction.response.send_message(f"Your new pet has been created!")

    #RENAME PET
    @app_commands.command(name="pet_rename", description="Rename your server's pet")
    @app_commands.guild_only()
    async def rename_pet(self, interaction: discord.Interaction, name: str):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.rename_pet(interaction.guild_id, name)
        await interaction.response.send_message(f"Your pet is now named **{name}**!")

    #SELECT PET
    PET_TYPES = ["Dog", "Cat", "Capybara", "Ferret", "Raccoon"]

    @app_commands.command(name="pet_change", description="Change what type of pet you have")
    @app_commands.choices(pet_type=[app_commands.Choice(name=t, value=t) for t in PET_TYPES])
    @app_commands.guild_only()
    async def change_pet(self, interaction: discord.Interaction, pet_type: app_commands.Choice[str]):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.set_pet_type(interaction.guild_id, pet_type.value)
        await interaction.response.send_message(f"You now have a **{pet_type.value}**!")
    
    #GET PET HUNGER
    @app_commands.command(name="pet_hunger", description="Check how hungry your pet is")
    @app_commands.guild_only()
    async def pet_hunger(self, interaction: discord.Interaction):
        pet = await database.get_pet(interaction.guild_id)
        if not pet:
            await interaction.response.send_message("Pet not found.", ephemeral=True)
            return

        hunger = await database.get_hunger(interaction.guild_id)
        await interaction.response.send_message(
            f"**{pet[1]}**\nHunger: {database.hunger_bar(hunger)}"
        )
    
    #FEED PET
    @app_commands.command(name="pet_feed", description="Feed your pet food from your inventory")
    @app_commands.describe(food="Choose the food to feed")
    @app_commands.choices(food=[
        app_commands.Choice(name="Regular Food", value=1),
        app_commands.Choice(name="Super Food", value=2),
        app_commands.Choice(name="Mega Food", value=3),
    ])
    @app_commands.guild_only()
    async def pet_feed(self, interaction: discord.Interaction, food: app_commands.Choice[int]):
        status, data = await database.feed_pet(
            interaction.guild_id, interaction.user.id, interaction.user.name, food.value
        )

        if status == "no_pet":
            await interaction.response.send_message("Pet not found.", ephemeral=True)
        elif status == "full":
            await interaction.response.send_message("Your pet is already full!", ephemeral=True)
        elif status == "no_item":
            await interaction.response.send_message(
                f"You don't have any {food.name}. Buy some with `/store_buy`.", ephemeral=True
            )
        else:
            item_name, new_hunger = data
            await interaction.response.send_message(
                f"{interaction.user.display_name} fed the pet **{item_name}**!\n"
                f"Hunger: {database.hunger_bar(new_hunger)}"
            )

async def setup(bot):
    await bot.add_cog(Pets(bot))