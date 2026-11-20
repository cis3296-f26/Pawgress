import discord
from discord.ext import commands, tasks
from commands.pet import Pet
import database
import pet

class HungerMonitor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hunger_alerted = {}

    async def cog_load(self):
        self.check_hunger.start()

    async def cog_unload(self):
        self.check_hunger.cancel()


    hunger_status = {
        0: "_I'm starving. I can't even move..._",                  #Hunger = 0
        1: "_Please feed me! I'm so hungry!_",                      #Hunger = 25
        2: "_I'm getting a bit hungry. A snack would be nice._"}    #Hunger = 50

    @tasks.loop(minutes=1)
    async def check_hunger(self):

        for guild in self.bot.guilds:

            pet = await database.get_pet(guild.id)
            channel_id = await database.get_alert_channel(guild.id)

            if not pet or not channel_id:
                continue

            channel = guild.get_channel(channel_id)

            if not channel:
                continue

            hunger = pet[3]

            # Determine which hunger category the pet is currently in
            if hunger == 0:
                current_state = 0
            elif hunger <= 25:
                current_state = 1
            elif hunger <= 50:
                current_state = 2
            else:
                current_state = None

            # Only notify when the hunger category changes
            if current_state is not None:
                last_state = self.hunger_alerted.get(guild.id)

                print(f"Guild: {guild.name}, Hunger: {hunger}, Current State: {current_state}, Last State: {last_state}")

                if current_state != last_state:
                    await channel.send(
                        f"@everyone **{pet[1]} The {pet[2]}**: "
                        f"{self.hunger_status[current_state]}",
                        allowed_mentions=discord.AllowedMentions(everyone=True)
                    )

                    self.hunger_alerted[guild.id] = current_state


    @check_hunger.before_loop
    async def before_check_hunger(self):
        await self.bot.wait_until_ready()

    
async def setup(bot):
    await bot.add_cog(HungerMonitor(bot))