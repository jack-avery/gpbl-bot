import discord
from discord import Button

from src.songs import Song


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
        raise NotImplementedError()

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
