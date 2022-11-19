import datetime
import os

from discord.ui import View

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


if __name__ == '__main__':
    client.run(os.getenv("DISCORD_SECRET_API"))
