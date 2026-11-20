from os import name
import discord
from discord import app_commands
from discord.ext import commands
from pet import Pet
from PIL import Image
import DisplayPet
import database

print(database.__file__)
print(dir(database))

FOOD_REACTIONS = {
    1: [
        "I mean yeah man whatever, Im starved over here and you offer me as close to nothing as it gets",
        "You know I eat earlier than this, let me get hungry like this again and Im leaving",
        "Regular food again, you could try mixing it up every once and awhile",
        "Thank you bubby"
    ],
    2: [
        "So hungry is me, my affliction it still remains",
        "Some years ago- never mind how long precisely- having little or no food in my stomach, "
        "I felt hunger, that is no more",
        "I am a thinking, breathing creature, and you have made this thinking, breathing "
        "creature, very happy today",
        "My tummy is so so full, I couldn't eat yet another morsel",
    ],
    3: [
        "Oh sweet ambrosia, how I needed this to rise from the ashes and soar again",
        "I could not have asked for anything more, you have made my week. NO! YOU HAVE MADE MY YEAR!",
        "Wonderful incredible amazing meal my dear, I will serve you to the ends of the earth",
        "My humble liege, while my appreciation to your offering holds no bounds, I am starved beyond belief. "
        "I can only nibble on this feast of kings"
    ]
}


def hunger_level(hunger: int):
    if hunger < 25:
        return 0
    elif hunger < 50:
        return 1
    elif hunger < 75:
        return 2
    else:
        return 3

def hunger_reaction(food_value: int, hunger: int):
    return FOOD_REACTIONS[food_value][hunger_level(hunger)]
class Pets(commands.Cog):

    disp = DisplayPet.DisplayPet()
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
    
    #FEED PET
    @app_commands.command(name="pet_feed", description="Feed your pet")
    @app_commands.describe(food="Choose what type of food to feed your pet")
    @app_commands.choices(food=[
        app_commands.Choice(name="Regular Food (15 coins)", value=1),
        app_commands.Choice(name="Super Food (20 coins)", value=2),
        app_commands.Choice(name="Mega Food (40 coins)", value=3)
    ])
    @app_commands.guild_only()
    async def pet_feed(self, interaction: discord.Interaction, food: app_commands.Choice[int]):
        
        pet = await database.get_pet(interaction.guild_id)
        if not pet:
            await interaction.response.send_message("Pet not found.", ephemeral=True)
            return

        user_id = await database.get_or_create_user(interaction.user.id, interaction.user.name)
        if not await database.remove_item(user_id, food.value):
            await interaction.response.send_message(f"You don't have **{food.name}**!", ephemeral=True)
            return

        hunger_before = await database.get_hunger(interaction.guild_id)
        reaction = hunger_reaction(food.value, hunger_before)
        hunger_restored = await database.get_item_hunger(food.value)
        new_hunger = await database.add_hunger(interaction.guild_id, hunger_restored)
        await interaction.response.send_message(
            f"**{interaction.user.display_name}** fed {pet[1]} **{food.name}**!\n"
            f"**{reaction}**\n"
            f"{database.hunger_bar(new_hunger)}"
        )

    #PET DISPLAY
    @app_commands.command(name="pet_display", description="Display the state of your pet")
    @app_commands.guild_only()
    async def pet_display(self, interaction: discord.Interaction):

        #(pet_id, pet_name, pet_type, pet_hunger) or None

        pet = await database.get_pet(interaction.guild_id)
        hunger = await database.get_hunger(interaction.guild_id)

        if not pet:
            await interaction.response.send_message("Pet not found.")
            return
        image_path = self.disp.display(hunger)
        file = discord.File(image_path, filename=image_path)

        embed = discord.Embed(
            title = f"{pet[1]} the {pet[2]}"
        )
            
        embed.add_field(
            name="Hunger",
            value=database.hunger_bar(hunger),
            inline=False
        )

        embed.set_thumbnail(url="attachment://image/pet_test/pet_test_0.jpg")

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

    @app_commands.command(name="pet_channel", description="Choose the channel where I post store and hunger alerts")
    @app_commands.describe(channel="The channel for notifications")
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.guild_only()
    async def set_alert_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await database.get_pet(interaction.guild_id):
            await interaction.response.send_message("Pet not found.", ephemeral=True)
            return

        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                f"I can't send messages in {channel.mention}. Pick another channel or give me permission there.",
                ephemeral=True,
            )
            return

        await database.set_alert_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"Alerts will now be posted in {channel.mention}!")


async def setup(bot):
    await bot.add_cog(Pets(bot))