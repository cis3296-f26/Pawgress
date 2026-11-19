import discord
from discord.ext import commands, tasks
import database

class HungerMonitor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hunger_alerted = {}

    async def cog_load(self):
        self.check_hunger.start()

    async def cog_unload(self):
        self.check_hunger.cancel()

    @tasks.loop(minutes=10)
    async def check_hunger(self):

        #Check each guild's pet for hunger alerts
        for guild in self.bot.guilds: 

            pet = await database.get_pet(guild.id)

            if pet is None:
                continue

                #pet[3] is hunger, pet[4] is hunger_alerted
            if pet[3] <= 25 and not self.hunger_alerted.get(guild.id, False):

                channel = guild.system_channel

                #Permissions error
                if channel is None or not channel.permissions_for(guild.me).send_messages:
                    channel = next(
                        (channel for channel in guild.text_channels
                        if channel.permissions_for(guild.me).send_messages),
                        None
                    )

                if channel is None:
                    continue

                await channel.send(
                    f"@everyone **{pet[1]} the {pet[2]}** says: _Please feed me!! I'm so hungry :(_",
                    allowed_mentions=discord.AllowedMentions(everyone=True)
                )

                self.hunger_alerted[guild.id] = True

            elif pet[3] > 25:
                self.hunger_alerted[guild.id] = False

    @check_hunger.before_loop
    async def before_check_hunger(self):
        await self.bot.wait_until_ready()

    
async def setup(bot):
    await bot.add_cog(HungerMonitor(bot))