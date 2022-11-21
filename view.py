import discord
from discord.ui import View, button, Button, Item
from discord import ButtonStyle, Interaction, Message


class HelloView(View):
    def __init__(self):
        super(HelloView, self).__init__(timeout=60)

    @button(style=ButtonStyle.green, label="Hi", emoji="👋", custom_id="hello")
    async def hi_callback(self, interaction: Interaction, but: Button):
        await interaction.response.edit_message(content="Welcome!\n"
                                                        "https://tenor.com/view/wave-hi-wave-hello-wave-hi-hello-gif-25155225",
                                                view=self)

    @button(style=ButtonStyle.red, label="Get off!", emoji="🖕", custom_id="getAway")
    async def go_callback(self, interaction: Interaction, but: Button):
        await interaction.response.edit_message(content="Get off!\n"
                                                        "https://tenor.com/view/get-away-from-me-wendy-testaburger-eric-cartman-south-park-back-off-gif-21150898",
                                                view=self)

    @button(style=ButtonStyle.blurple, label="You are you?!", emoji="🤔", custom_id="whoAreYou")
    async def wau_callback(self, interaction: Interaction, but: Button):
        await interaction.response.edit_message(content="Who are you?\n"
                                                        "https://tenor.com/view/who-are-you-gif-21457791",
                                                view=self)


class ClearView(View):
    def __init__(self, interaction: Interaction, limit=None):
        super(ClearView, self).__init__(timeout=5)
        self.interaction = interaction
        self.limit = limit

    @button(style=ButtonStyle.green, emoji="✅", custom_id="yes")
    async def yes_callback(self, interaction: Interaction, but: Button):
        if self.limit:
            await interaction.channel.purge(limit=self.limit + 1)
        else:
            await interaction.channel.purge(limit=self.limit)

    @button(style=ButtonStyle.red, emoji="💀", custom_id="no")
    async def no_callback(self, interaction: Interaction, but: Button):
        await interaction.response.send_message("messages won't be cleared.", ephemeral=True)
        await interaction.channel.purge(limit=1)

    async def on_timeout(self) -> None:
        try:
            await self.interaction.delete_original_response()
        except discord.NotFound:
            print("message already deleted")


class PollView(View):
    def __init__(self, interaction: Interaction, question):
        super(PollView, self).__init__(timeout=600)
        self.interaction = interaction
        self.question = question
        self.edit = ""
        self.agree = []
        self.disagree = []

    @button(style=ButtonStyle.green, emoji="👍", custom_id="PollYes")
    async def yes_callback(self, interaction: Interaction, but: Button):
        if interaction.user.name not in self.agree:
            if interaction.user.name in self.disagree:
                self.disagree.remove(interaction.user.name)
            self.agree.append(interaction.user.name)
        else:
            self.agree.remove(interaction.user.name)
        await interaction.response.edit_message(view=self, embed=self.update_embed(interaction.user.name))

    @button(style=ButtonStyle.red, emoji="👎", custom_id="PollNo")
    async def no_callback(self, interaction: Interaction, but: Button):
        if interaction.user.name not in self.disagree:
            if interaction.user.name in self.agree:
                self.agree.remove(interaction.user.name)
            self.disagree.append(interaction.user.name)
        else:
            self.disagree.remove(interaction.user.name)
        await interaction.response.edit_message(view=self, embed=self.update_embed(interaction.user.name))

    def update_embed(self, author: str):
        embed = discord.Embed(title=self.question, description=f"Question started by {author}",
                              colour=discord.Colour.random())
        embed.set_author(name=author)
        embed.add_field(name="Agreed", value=self.format_string(self.agree))
        embed.add_field(name="Disagreed", value=self.format_string(self.disagree))
        return embed

    @staticmethod
    def format_string(array: []):
        tmp = "".join(user + '\n' for user in array)
        return tmp if tmp != "" else "None"
