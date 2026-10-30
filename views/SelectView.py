import discord

#SelectView for study methods. If we want to add SelectView for pet selection we will have to update this

class SelectView(discord.ui.View):

    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        self.user = user
        self.choice = None

    
    #Ensure that only the user who initiated the command can interact with the dropdown
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("This is not your selection menu!", ephemeral=True)
            return False
        return True

    @discord.ui.select(
        placeholder="Select",
        options=[
            discord.SelectOption(label="Pomodoro", value="pomodoro", description="Study for 25 and break for 5"),
            discord.SelectOption(label="90minblock", value="90minblock", description="Study for 60, review for 20"),
            discord.SelectOption(label="Freeflow", value="freeflow", description="Study with no interruptions")
        ],)

    #Callback for dropdown (runs when a user picks an option)
    async def select_method(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.choice = select.values[0]
        await interaction.response.defer()

        #Stop listening for interactions
        self.stop()




