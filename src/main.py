# main.py
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import sys

from src.songs import SongsHandler

from cogs.user import UserCog
from cogs.admin import AdminCog

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_VOICE_CHANNEL_ID = int(os.getenv("DISCORD_VOICE_CHANNEL_ID"))
SONGS_LOCATION = os.getenv("SONGS_LOCATION")
SONGS_LOOKAHEAD = int(os.getenv("SONGS_LOOKAHEAD"))
SKIP_VOTE_PERCENTAGE = int(os.getenv("SKIP_VOTE_PERCENTAGE"))

log_handlers = []
formatter = logging.Formatter(
    "%(asctime)s | %(module)s [%(levelname)s] %(message)s",
)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
log_handlers.append(stdout_handler)
logging.basicConfig(handlers=log_handlers, level=logging.DEBUG)


class DiscordBot(commands.Bot):
    skip_voters = list[int]

    def __init__(self):
        intents = discord.Intents()
        intents.guilds = True
        intents.guild_messages = True
        intents.voice_states = True

        super().__init__(command_prefix="b$", intents=intents)
        self.SONGS = SongsHandler(folder=SONGS_LOCATION, lookahead=SONGS_LOOKAHEAD)
        self.SETUP = False

    async def on_ready(self):
        if not self.SETUP:
            logging.info("Connected to Discord")

            self.CHANNEL = self.get_channel(DISCORD_VOICE_CHANNEL_ID)

            guilds = [guild async for guild in client.fetch_guilds(limit=150)]
            await self.add_cog(AdminCog(self))
            await self.add_cog(UserCog(self))
            for guild in guilds:
                self.tree.copy_global_to(guild=discord.Object(id=guild.id))
            await self.tree.sync()

            logging.info("Ready!")
            logging.info(f"Current Guilds: {', '.join([g.name for g in self.guilds])}")
            self.SETUP = True

        await self.CHANNEL.connect()
        asyncio.ensure_future(self.play_forever())

    async def play_next(self):
        session: discord.VoiceClient = self.CHANNEL.guild.voice_client

        if not session.is_connected():
            await self.CHANNEL.connect()

        if session.is_playing():
            session.stop()

        self.CURRENT_SONG = self.SONGS.next()
        logging.info(f"Now playing: {self.CURRENT_SONG}")

        self.skip_voters = []
        session.play(
            discord.FFmpegPCMAudio(executable="ffmpeg", source=self.CURRENT_SONG.path)
        )

        embed = discord.Embed(
            color=discord.Color.blurple(),
            description=f"Now playing: {self.CURRENT_SONG}",
        )
        await self.CHANNEL.send(embed=embed)

    async def play_forever(self):
        session: discord.VoiceClient = self.CHANNEL.guild.voice_client

        while True:
            if session.is_playing():
                await asyncio.sleep(1)
                continue

            await self.play_next()

    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        # user disconnected
        if not (before.channel == self.CHANNEL and after is None):
            return

        if member.id in self.skip_voters:
            self.skip_voters.remove(member.id)

        if len(self.CHANNEL.members) == 1:
            return

        if (
            len(client.skip_voters) / (len(client.CHANNEL.members) - 1)
        ) > SKIP_VOTE_PERCENTAGE / 100:
            await client.play_next()

            embed = discord.Embed(
                color=discord.Color.green(),
                description=f"The active skip vote passed due to a user disconnecting. Now playing: {client.CURRENT_SONG}",
            )
            await self.CHANNEL.send(embed=embed)


client = DiscordBot()


@client.tree.command(name="help", description="See available commands")
async def _help(interaction: discord.Interaction) -> None:
    commands = await client.tree.fetch_commands()
    listing = "- " + "\n- ".join(
        [f"</{c.name}:{c.id}>: {c.description}" for c in commands]
    )

    embed = discord.Embed(color=discord.Color.magenta(), description=listing)
    embed.set_author(
        name="Commands",
        icon_url=client.user.display_avatar.url,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="np", description="See information about current song")
async def _np(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        color=discord.Color.blurple(),
        description=f"The current song is: {client.CURRENT_SONG}",
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="q", description="See the upcoming songs queue")
async def _q(interaction: discord.Interaction) -> None:
    listing = "\n".join([f"`{i+1}`: {s}" for i, s in enumerate(client.SONGS.up_next)])

    embed = discord.Embed(
        color=discord.Color.blurple(),
        description=listing,
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="skip", description="Vote to skip the current song")
async def _skip(interaction: discord.Interaction) -> None:
    if interaction.user.id in client.skip_voters:
        embed = discord.Embed(
            color=discord.Color.red(), description="You have already voted to skip!"
        )
        await interaction.response.send_message(embed=embed)

    if interaction.user not in client.CHANNEL.members:
        embed = discord.Embed(
            color=discord.Color.red(),
            description="You're not in the voice channel!",
        )
        await interaction.response.send_message(embed=embed)

    client.skip_voters.append(interaction.user.id)
    logging.info(
        f"{interaction.user.display_name} ({interaction.user.id}) voted to skip"
    )

    if (
        len(client.skip_voters) / (len(client.CHANNEL.members) - 1)
    ) > SKIP_VOTE_PERCENTAGE / 100:
        await client.play_next()

        embed = discord.Embed(
            color=discord.Color.green(),
            description=f"Skip vote passed. Now playing: {client.CURRENT_SONG}",
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            color=discord.Color.blurple(),
            description="You have voted to skip the current song.",
        )
        await interaction.response.send_message(embed=embed)


client.run(DISCORD_BOT_TOKEN)
