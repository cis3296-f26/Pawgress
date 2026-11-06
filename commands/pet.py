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
    @app_commands.command(name="create_pet", description="Create a new pet for this server")
    @app_commands.guild_only()
    async def create_pet(self, interaction: discord.Interaction):
        if await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("This server already has a pet!")
            return
        
        await database.create_pet(
            # placeholders
            interaction.guild_id, name="No name", pet_type="Dog"
        )
        await interaction.response.send_message("Your new pet has been created!")

    #RENAME PET
    @app_commands.command(name="rename_pet", description="Rename your server's pet")
    @app_commands.guild_only()
    async def rename_pet(self, interaction: discord.Interaction, name: str):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.rename_pet(interaction.guild_id, name)
        await interaction.response.send_message(f"Your pet is now named **{name}**!")

    #SELECT PET
    PET_TYPES = ["Aj", "Bryan", "Emma", "Evan", "Walter"]

    @app_commands.command(name="change_pet", description="Change what type of pet you have")
    @app_commands.choices(pet_type=[app_commands.Choice(name=t, value=t) for t in PET_TYPES])
    @app_commands.guild_only()
    async def change_pet(self, interaction: discord.Interaction, pet_type: app_commands.Choice[str]):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.set_pet_type(interaction.guild_id, pet_type.value)
        await interaction.response.send_message(f"You now have a **{pet_type.value}**!")


async def setup(bot):
    await bot.add_cog(Pets(bot))