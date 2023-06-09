import os
from dataclasses import dataclass
from random import shuffle

from request import get_json
from tools import remove_key_by_value, is_categories_allowed

from view import *
from dotenv import load_dotenv

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
    await interaction.response.send_message(f"pong! bot latency: **{int(client.latency * 1000)}** ms\n")


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
            if clear < 1:
                await interaction.response.send_message("Sorry, but I can't do that :)", ephemeral=True)
                return
            await interaction.response.send_message(f"Are you sure you want to clear {clear} "
                                                    f"{'message' if clear < 2 else 'messages'}?",
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


@tree.command(name="friendsteam", description="Return the number of friend in your steam account")
async def get_friends_steam(interaction: Interaction, id_steam: str):
    await interaction.response.send_message("Fetching data...")
    data = await get_json(
        f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={os.getenv('STEAM_API_KEY')}&steamid={id_steam}&relationship=friend")
    await interaction.edit_original_response(content=f"You have {len(data['friendslist']['friends'])} friends!")


@tree.command(name="gamesteam", description="Return the number of games in steam store")
async def number_of_game_steam(interaction: Interaction):
    await interaction.response.send_message("Fetching data... can take a while..")
    data = await get_json("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json")
    await interaction.edit_original_response(content=f"There are {len(data['applist']['apps'])} games in the store")


@tree.command(name="steamcategory", description="Retrieve games according to categories.")
async def game_by_categories(interaction: Interaction, categories_steam: str, limit: int = 2):

    async def get_game_by_categories(data, category: [], limit: int):
        steam_games = {}

        to_reach = 0
        tmp: list = remove_key_by_value(data['applist']['apps'], "")
        shuffle(tmp)

        for (i, game) in enumerate(tmp):
            if to_reach == limit or i == 250:
                break
            i += 1
            fetch = await get_json(f"https://store.steampowered.com/api/appdetails?appids={game['appid']}")

            try:
                if any(item in fetch[str(game['appid'])]['data']['name'].lower() for item in ["demo", "dlc"]):
                    continue
                if all(item in [x['description'].lower() for x in fetch[str(game['appid'])]['data']['genres']] for item in category):
                    steam_games[fetch[str(game['appid'])]['data']['name']] = {
                        "header_image": fetch[str(game['appid'])]['data']['header_image'],
                        "date": fetch[str(game['appid'])]['data']['release_date']['date'],
                        "is_free": fetch[str(game['appid'])]['data']['is_free'],
                        "url": f"https://store.steampowered.com/app/{str(fetch[str(game['appid'])]['data']['steam_appid'])}/{fetch[str(game['appid'])]['data']['name'].replace(' ', '_')}"
                    }
                    to_reach += 1
            except Exception as e:
                print(e)
            if i % 10 == 0:
                await interaction.edit_original_response(
                    content=f"Fetching data... may take a while.. ({max((to_reach / limit) * 100, (i / 250) * 100):.2f}%)")
        await interaction.edit_original_response(content="Fetching data... may take a while.. 100.00%")
        return steam_games

    def embed_games(games: {}) -> [discord.Embed]:
        embeds = []

        for game in games:
            embed = discord.Embed(colour=discord.Colour.random(), title=game)
            embed.add_field(name="Game page", value=f"[Link to page]({games[game]['url']})", inline=False)
            embed.set_image(url=games[game]['header_image'])
            embed.add_field(name="Is free", value=games[game]['is_free'])
            embed.add_field(name="Date", value=games[game]['date'])
            embeds.append(embed)
        return embeds

    categories_steam = categories_steam.lower().strip().split(',')
    if not is_categories_allowed(categories_steam):
        return await interaction.response.send_message("One of the tags in not in the list, please check the wiki to have a look to allowed tags :)")

    await interaction.response.send_message("Fetching data... may take a while.. (0%)")
    data = await get_json("http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json")
    games = await get_game_by_categories(data, categories_steam, limit)
    if len(games) == 0:
        await interaction.edit_original_response(content="Aight, I haven't found games according to your tags ¯\_(ツ)_/¯")
    else:
        await interaction.edit_original_response(embeds=embed_games(games))


@tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message(error, ephemeral=True)
    else:
        raise error


if __name__ == '__main__':
    client.run(os.getenv("DISCORD_SECRET_API"))
