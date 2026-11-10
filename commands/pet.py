from os import name
import display_pet
import discord
import database
from discord import app_commands
from discord.ext import commands
from pet import Pet
from PIL import Image

print(database.__file__)
print(dir(database))
class Pets(commands.Cog):

    disp = display_pet.DisplayPet()
    def __init__(self, bot):
        self.bot = bot


    #RENAME PET
    @app_commands.command(name="pet_rename", description="Rename your server's pet")
    @app_commands.guild_only()
    async def rename_pet(self, interaction: discord.Interaction, name: str):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return

        await database.rename_pet(interaction.guild_id, name)
        await interaction.response.send_message(f"Your pet is now named **{name}**!")

    @app_commands.command(name="display_pet", description="display the state of your pet")
    @app_commands.guild_only()
    async def display_pet(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return
        image_path = self.disp.display()
        file = discord.File(image_path, filename="pet.png")

        embed = discord.Embed(
            title="Your pet:",
            color=discord.Color.red(),
        )
        embed.set_image(url="attachment://pet.png")

        await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(name="inc_h", description="evil test")
    @app_commands.guild_only()
    async def inc_h(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return
        self.disp.hunger_increase()

    @app_commands.command(name="dec_h", description="evil test")
    @app_commands.guild_only()
    async def inc_d(self, interaction: discord.Interaction):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.")
            return
        self.disp.hunger_decrease()

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
        await interaction.response.send_message(f"Your pet is now a **{pet_type.value}**!")


    #DISPLAY PET (to-do)


async def setup(bot):
    await bot.add_cog(Pets(bot))