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

    # Commands here. We can add more commands like name, feed, etc.

    #pet creation command
    @app_commands.command(name="create_pet", description="Create a new pet for this channel")
    @app_commands.guild_only()
    async def create_pet(self, interaction: discord.Interaction):
        if await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("This server already has a pet!")
            return

        user_id = await database.get_or_create_user(
            interaction.user.id, interaction.user.name
        )
        await database.create_pet(
            interaction.guild_id, user_id, name="No name", pet_type="Dog" #placeholders
        )
        await interaction.response.send_message("Your new pet has been created!")

    #rename pet command
    @app_commands.command(name="rename_pet", description="Rename your server's pet")
    @app_commands.guild_only()
    async def rename_pet(self, interaction: discord.Interaction, name: str):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.rename_pet(interaction.guild_id, name)
        await interaction.response.send_message(f"Your pet is now named **{name}**!")

    #help command
    @app_commands.command(name="help", description="list commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("/help - list commands\n/create_pet - create a new pet\n/rename_pet - rename your pet", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Pets(bot))