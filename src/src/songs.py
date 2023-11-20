import ffmpeg
import yaml
import math
import random
import re

VALID_FILE = re.compile(r"[a-zA-Z0-9\_\-]+\.(?:wav|mp3)")


class Song:
    file: str
    path: str

    rapper1: str
    rapper2: str
    league: str

    length: str
    length_secs: int

    __folder: str

    def __init__(
        self, file: str, rapper1: str, rapper2: str, league: str, folder: str = "songs"
    ):
        if not VALID_FILE.match(file):
            raise ValueError(f"invalid filename: {file}")

        self.path = f"{folder}/{file}"
        self.rapper1 = rapper1
        self.rapper2 = rapper2
        self.league = league

        self.file = file
        self.__folder = folder

        self.length_secs = round(float(ffmpeg.probe(self.path)["format"]["duration"]))
        m = math.floor(self.length_secs / 60)
        s = self.length_secs % 60
        s = f"0{s}" if s < 10 else s
        self.length = f"{m}:{s}"

    def __repr__(self) -> str:
        return f'songs.Song("{self.file}", "{self.rapper1}", "{self.rapper2}", "{self.league}", "{self.__folder}")'

    def __str__(self) -> str:
        return f"**{self.rapper1}** vs **{self.rapper2}** - {self.league} (`{self.length}`)"

    json_sample: str = (
        "# sample entry\n"
        + "# filename.mp3:\n"
        + "#   rapper1: rapper name\n"
        + "#   rapper2: rapper name\n"
        + "#   league: league name\n\n"
    )

    def json(self) -> dict:
        return {
            "rapper1": self.rapper1,
            "rapper2": self.rapper2,
            "league": self.league,
        }


class SongsHandler:
    folder: str
    lookahead: int

    songs: dict[str, Song]
    up_next: list[Song]
    __choose_songs: list[Song]

    def __init__(self, folder: str, lookahead: int):
        self.folder = folder
        self.lookahead = lookahead
        self.reload()

    def choose(self, count: int = 1):
        """Attempt to populate `count` slots of `up_next`.

        :param count: Slots to populate
        """
        for _ in range(count):
            if len(self.__choose_songs) == 0:
                return

            song = random.choice(self.__choose_songs)
            self.__choose_songs.remove(song)
            self.up_next.append(song)

    def add(self, song: Song):
        """Add `song` to this `SongHandler`.

        :param song: The `Song` object to add
        """
        if song.file in self.songs:
            raise KeyError(f"{song.file} already exists")

        self.songs[song.file] = song
        self.__choose_songs.append(song)

        if len(self.up_next) < self.lookahead:
            self.choose()

    def remove(self, song: str) -> Song:
        """Remove `song` from this `SongHandler`.

        Returns the song object removed.

        :param song: The song to remove
        :returns: The `Song` that got removed
        """
        if song not in self.songs:
            raise KeyError(f"{song} does not exist")

        song = self.songs.pop(song)
        if song in self.up_next:
            self.up_next.remove(song)
            self.choose()
        elif song in self.__choose_songs:
            self.__choose_songs.remove(song)

        return song

    def next(self) -> Song:
        """Grab the next song in `up_next` and remove it from the queue."""
        if len(self.up_next) == 0:
            return None

        song = self.up_next.pop(0)
        self.__choose_songs.append(song)
        self.choose()

        return song

    def reload(self):
        """Reload this `SongsHandler`'s song data from disk."""
        self.songs = {}
        self.__choose_songs = []
        self.up_next = []

        with open(f"{self.folder}/meta.yml") as meta:
            songs: dict = yaml.safe_load(meta.read())

        if not songs:
            return

        for file, s in songs.items():
            song = Song(file, s["rapper1"], s["rapper2"], s["league"], self.folder)
            self.songs[file] = song
        self.__choose_songs = [s for s in self.songs.values()]
        self.choose(self.lookahead)

    def save(self):
        """Save this `SongsHandler`'s song data to disk."""
        out: dict[str, Song] = self.songs.copy()
        for file, song in out.items():
            out[file] = song.json()

        out_s = Song.json_sample
        out_s += yaml.dump(out)

        with open(f"{self.folder}/meta.yml", "w") as meta:
            meta.write(out_s)
