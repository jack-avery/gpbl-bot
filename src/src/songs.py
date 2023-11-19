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
        self, file: str, rapper1: str, rapper2: str, league: str, folder: str = "."
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
        self.length = f"{m}:{s}"

    def __repr__(self) -> str:
        return f'songs.Song("{self.file}", "{self.rapper1}", "{self.rapper2}", "{self.league}", "{self.__folder}")'

    def __str__(self) -> str:
        return f"**{self.rapper1}** vs **{self.rapper2}** - {self.league} (`{self.length}`)"

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
        for _ in range(count):
            if len(self.__choose_songs) == 0:
                raise ValueError("no more distinct songs to populate lookahead")

            song = random.choice(self.__choose_songs)
            self.__choose_songs.remove(song)
            self.up_next.append(song)

    def add(self, song: Song):
        self.songs[song.file] = song
        self.__choose_songs.append(song)

    def remove(self, song: str) -> Song:
        song = self.songs.pop(song)
        if song in self.up_next:
            self.up_next.remove(song)
            self.choose()
        elif song in self.__choose_songs:
            self.__choose_songs.remove(song)

        return song

    def next(self) -> Song:
        song = self.up_next.pop(0)
        self.choose()
        self.__choose_songs.append(song)

        return song

    def reload(self):
        self.songs = {}
        self.__choose_songs = []
        self.up_next = []

        with open(f"{self.folder}/meta.yml") as meta:
            songs: dict = yaml.safe_load(meta.read())

        if len(songs) < self.lookahead:
            raise ValueError("lookahead too large: not enough songs to populate")

        for file, s in songs.items():
            song = Song(file, s["rapper1"], s["rapper2"], s["league"], self.folder)
            self.songs[file] = song
        self.__choose_songs = [s for s in self.songs.values()]
        self.choose(self.lookahead)

    def save(self):
        out: dict[str, Song] = self.songs.copy()
        for file, song in out.items():
            out[file] = song.json()

        with open(f"{self.folder}/meta.yml", "w") as meta:
            meta.write(yaml.dump(out))
