import os

import discord
from discord.ext import commands
from discord import app_commands

from src.songs import Song, VALID_FILE
from cogs.base_cog import SongsListView


class AdminListView(SongsListView):
    def __init__(self, songs: dict[str, Song]):
        super().__init__(songs)

    def create_embed(self, page: int) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.blurple())

        song: Song
        for i, song in enumerate(self.songs[page]):
            num = (page * 10) + i + 1
            embed.add_field(name=f"`{num}`: `{song.file}`", value=song)

        embed.set_footer(text=f"Page {page+1} of {len(self.songs)}")
        return embed


class AdminCog(commands.Cog):
    group = app_commands.Group(
        name="admin", description="Commands reserved for 'admin' users"
    )

    def __init__(self, bot):
        self.bot = bot

    @group.command(name="list", description="List songs")
    @app_commands.checks.has_permissions(administrator=True)
    async def _list(self, interaction: discord.Interaction):
        view = AdminListView(self.bot.SONGS.songs)
        embed = view.create_embed(0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @_list.error
    async def _list_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(error, ephemeral=True)
            return

    @group.command(name="remove", description="Remove a song")
    @app_commands.checks.has_permissions(administrator=True)
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
        await interaction.response.send_message(embed=embed)

    @_remove.error
    async def _remove_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(error, ephemeral=True)
            return

    @group.command(name="add", description="Add a new song")
    @app_commands.checks.has_permissions(administrator=True)
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
        await interaction.response.send_message(embed=embed)

    @_add.error
    async def _add_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(error, ephemeral=True)
            return

    @group.command(name="edit", description="Edit a song's data")
    @app_commands.checks.has_permissions(administrator=True)
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
        await interaction.response.send_message(embed=embed)

    @_edit.error
    async def _edit_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(error, ephemeral=True)
            return

    @group.command(name="skip", description="Skip the current song")
    @app_commands.checks.has_permissions(administrator=True)
    async def _skip(self, interaction: discord.Interaction):
        await self.bot.play_next()

        embed = discord.Embed(
            color=discord.Color.green(),
            description=f"Administrator forced skip. Now playing: {self.bot.CURRENT_SONG}",
        )
        await interaction.response.send_message(embed=embed)

    @_skip.error
    async def _skip_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(error, ephemeral=True)
            return
