from discord.ui import View, button, Button
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
        await interaction.response.edit_message(content="You are you?\n"
                                                        "https://tenor.com/view/who-are-you-gif-21457791",
                                                view=self)
