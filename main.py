import datetime
import os

from view import *
from dotenv import load_dotenv
from dataclasses import dataclass

import discord
from discord import app_commands
from discord import Interaction

load_dotenv(dotenv_path='./.env')


@dataclass
class Aclient(discord.Client):
    _synced = False

    def __init__(self):
        super().__init__(intents=discord.Intents.default())

    async def on_ready(self):
        await self.wait_until_ready()
        if not self._synced:
            await tree.sync()
            self._synced = True
        print(f"{self.user} in online.")

    async def on_member_join(self, message: discord.Message):
        if message.author.name != self.user.name:
            await message.reply("A new person!", view=HelloView())


client = Aclient()
tree = app_commands.CommandTree(client)


@tree.command(name="ping", description="pong!")
async def pong(interaction: Interaction):
    command_latency = (datetime.datetime.now(datetime.timezone.utc) - interaction.created_at).microseconds
    await interaction.response.send_message(f"pong! bot latency: **{int(client.latency * 1000)}** ms\n"
                                            f"Whole command latency: **{command_latency}** ms")


@tree.command(name="clear", description="clear message")
@app_commands.checks.bot_has_permissions(administrator=True)
async def to_clear(interaction: Interaction, clear: str) -> None:
    if interaction.user.guild_permissions.administrator:
        if clear == "all":
            await interaction.response.send_message("Are you sure you want to clear all messages?",
                                                    view=ClearView(interaction))
            return
        try:
            clear = int(clear)
            await interaction.response.send_message(f"Are you sure you want to clear {clear} messages?",
                                                    view=ClearView(interaction, clear))
        except ValueError:
            await interaction.response.send_message("please provide a number!", ephemeral=True)
    else:
        await interaction.response.send_message("You must be an administrator to run this command!", ephemeral=True)


@tree.command(name="poll", description="poll with closed questions")
async def create_poll(interaction: Interaction, question: str):
    view = PollView(interaction, question)
    await interaction.response.send_message(view=view,
                                            embed=view.update_embed(interaction.user.name))


@tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message(error, ephemeral=True)
    else:
        raise error


if __name__ == '__main__':
    client.run(os.getenv("DISCORD_SECRET_API"))
