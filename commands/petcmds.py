import discord
from discord import app_commands
from discord.ext import commands
from pet import Pet, PET_TYPES

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

    @app_commands.command(name="select_pet_type", description="Choose what kind of animal your pet is")
    @app_commands.describe(animal_type="The kind of animal your pet will be")
    @app_commands.choices(animal_type=[app_commands.Choice(name=t, value=t) for t in PET_TYPES]) # Shows a dropdown in discord so users can only pick valid types
    async def select_pet_type(self, interaction: discord.Interaction, animal_type: app_commands.Choice[str]):

        key = interaction.channel_id # Same key as create_pet

        if key not in self.bot.pets:
            await interaction.response.send_message("You don't have a pet yet! Use /create_pet first.", ephemeral=False)
        else:
            self.bot.pets[key].animal_type = animal_type.value
            await interaction.response.send_message(f"Your pet is now a {animal_type.value}!", ephemeral=False)

    @app_commands.command(name="help", description="list commands")

    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("/help - list commands\n/create_pet - create a new pet\n/select_pet_type - choose what animal your pet is", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Pets(bot))