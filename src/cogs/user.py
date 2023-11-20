import os

import discord
from discord.ext import commands
from discord import app_commands, Button

from src.songs import Song, VALID_FILE
from cogs.base_cog import SongsListView


class UserListView(SongsListView):
    def __init__(self, songs: dict[str, Song]):
        super().__init__(songs)

    def create_embed(self, page: int) -> discord.Embed:
        song: Song
        listing: str = ""
        for i, song in enumerate(self.songs[page]):
            num = (page * 10) + i + 1
            listing += f"`{num}`: {song}\n"

        embed = discord.Embed(colour=discord.Colour.blurple(), description=listing)
        embed.set_footer(text=f"Page {page+1} of {len(self.songs)}")
        return embed


class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list", description="List songs")
    async def _list(self, interaction: discord.Interaction):
        view = UserListView(self.bot.SONGS.songs)
        embed = view.create_embed(0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
