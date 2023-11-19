import os

import discord
from discord.ext import commands
from discord import app_commands, Button

from src.songs import Song, VALID_FILE


class SongsListView(discord.ui.View):
    PAGE_SIZE = 10

    def __init__(self, songs: dict[str, Song]):
        super().__init__()
        self.page = 0

        songs = [s for s in songs.values()]
        self.songs: list[list[Song]] = [
            songs[i : i + self.PAGE_SIZE] for i in range(0, len(songs), self.PAGE_SIZE)
        ]

        self.set_nav()

    def create_embed(self, page: int) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.blurple())

        song: Song
        for song in self.songs[page]:
            embed.add_field(name=f"`{song.file}`", value=song)

        embed.set_footer(text=f"Page {page+1} of {len(self.songs)}")

        return embed

    def set_nav(self):
        for child in self.children:
            child: Button
            if type(child) == discord.ui.Button:
                if child.custom_id == "prev":
                    if self.page == 0:
                        child.disabled = True
                    elif child.disabled and self.page != 0:
                        child.disabled = False

                elif child.custom_id == "next":
                    if self.page == len(self.songs) - 1:
                        child.disabled = True
                    elif child.disabled and self.page != len(self.songs) - 1:
                        child.disabled = False

    @discord.ui.button(
        custom_id="prev", emoji="⬅️", style=discord.ButtonStyle.secondary
    )
    async def prev_callback(
        self,
        interaction: discord.Interaction,
        button: discord.Button,
    ):
        self.page -= 1
        self.set_nav()
        await interaction.response.edit_message(
            embed=self.create_embed(self.page), view=self
        )

    @discord.ui.button(
        custom_id="next", emoji="➡️", style=discord.ButtonStyle.secondary
    )
    async def next_callback(
        self,
        interaction: discord.Interaction,
        button: discord.Button,
    ):
        self.page += 1
        self.set_nav()
        await interaction.response.edit_message(
            embed=self.create_embed(self.page), view=self
        )


class AdminCog(commands.Cog):
    group = app_commands.Group(
        name="admin", description="Commands reserved for 'admin' users"
    )

    def __init__(self, bot):
        self.bot = bot

    @group.command(name="list", description="List songs")
    @commands.has_permissions(manage_guild=True)
    async def _list(self, interaction: discord.Interaction):
        view = SongsListView(self.bot.SONGS.songs)
        embed = view.create_embed(0)
        await interaction.response.send_message(
            embed=embed,
            view=view,
        )

    @group.command(name="remove", description="Remove a song")
    @commands.has_permissions(manage_guild=True)
    @discord.app_commands.describe(
        file="file to remove",
    )
    async def _remove(
        self,
        interaction: discord.Interaction,
        file: str,
    ):
        if not VALID_FILE.match(file):
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description="File is not a valid file. Names must be alphanumeric with hyphens (-) and underscores (_), and be a `.wav` or `.mp3`.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if file not in self.bot.SONGS.songs:
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description=f"No audio file with the name {file} exists.",
            )
            embed.set_footer(
                "Try using `/admin list` to see a list of songs and their filenames"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        song: Song = self.bot.SONGS.remove(file)
        self.bot.SONGS.save()
        os.remove(song.path)

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=f"Removed `{file}` ({song}).",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="add", description="Add a new song")
    @commands.has_permissions(manage_guild=True)
    @discord.app_commands.describe(
        rapper1="rapper name for rapper 1",
        rapper2="rapper name for rapper 2",
        league="league name",
        audio="audio file",
    )
    async def _add(
        self,
        interaction: discord.Interaction,
        rapper1: str,
        rapper2: str,
        league: str,
        audio: discord.Attachment,
    ):
        if not VALID_FILE.match(audio.filename):
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description="File is not a valid file. Names must be alphanumeric with hyphens (-) and underscores (_), and be a `.wav` or `.mp3`.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if audio.filename in self.bot.SONGS.songs:
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description=f"An audio file with the name {audio.filename} already exists.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        file_path = f"{self.bot.SONGS.folder}/{audio.filename}"
        await audio.save(file_path)
        song = Song(audio.filename, rapper1, rapper2, league, self.bot.SONGS.folder)
        self.bot.SONGS.add(song)
        self.bot.SONGS.save()

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=f"Added `{audio.filename}` as {song}.",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="edit", description="Edit a song's data")
    @commands.has_permissions(manage_guild=True)
    @discord.app_commands.describe(
        file="file to modify",
        rapper1="rapper name for rapper 1",
        rapper2="rapper name for rapper 2",
        league="league name",
    )
    async def _edit(
        self,
        interaction: discord.Interaction,
        file: str,
        rapper1: str = None,
        rapper2: str = None,
        league: str = None,
    ):
        if not VALID_FILE.match(file):
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description="File is not a valid file. Names must be alphanumeric with hyphens (-) and underscores (_), and be a `.wav` or `.mp3`.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if file not in self.bot.SONGS.songs:
            embed = discord.Embed(
                colour=discord.Colour.red(),
                description=f"No audio file with the name {file} exists.",
            )
            embed.set_footer(
                "Try using `/admin list` to see a list of songs and their filenames"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        song: Song = self.bot.SONGS.songs[file]

        if rapper1:
            song.rapper1 = rapper1

        if rapper2:
            song.rapper2 = rapper2

        if league:
            song.league = league

        self.bot.SONGS.save()

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=f"Modified `{file}`, is now {song}.",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
