import discord
from discord import app_commands
from discord.ext import commands
from pet import Pet

class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Commands here. We can add more commands like name, feed, etc.
    @app_commands.command(name="create_pet", description="Create a new pet for this channel")

    async def create_pet(self, interaction: discord.Interaction):
    
        key = interaction.channel_id # Eventually we may have to change this to guild_id

        if key in self.bot.pets:
            await interaction.response.send_message("You already have a pet!", ephemeral=False) # Ephemeral false means that the message will be visible to everyone in the channel
        else:
            new_pet = Pet(name="No name", animal_type="Dog") # Placeholders for now idk
            self.bot.pets[key] = new_pet
            await interaction.response.send_message("Your new pet has been created!", ephemeral=False)

    @app_commands.command(name="rename_pet", description="Rename your pet")
    async def rename_pet(self, interaction: discord.Interaction, name: str):
        key = interaction.channel_id

        if key not in self.bot.pets:
            await interaction.response.send_message("Pet not found.", ephemeral=False)
            return

        self.bot.pets[key].name = name
        await interaction.response.send_message(f"Your pet is now named **{name}**!", ephemeral=False)

    @app_commands.command(name="help", description="list commands")

    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("/help - list commands\n/create_pet - create a new pet\n/rename_pet - rename your pet", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Pets(bot))