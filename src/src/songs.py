import ffmpeg
import yaml
import math
import random


class Song:
    path: str

    rapper1: str
    rapper2: str
    league: str

    length: str
    length_secs: int

    def __init__(
        self, file: str, rapper1: str, rapper2: str, league: str, folder: str = "."
    ):
        self.path = f"{folder}/{file}"
        self.rapper1 = rapper1
        self.rapper2 = rapper2
        self.league = league

        self.length_secs = round(float(ffmpeg.probe(self.path)["format"]["duration"]))
        m = math.floor(self.length_secs / 60)
        s = self.length_secs % 60
        self.length = f"{m}:{s}"

    def __repr__(self) -> str:
        return f"**{self.rapper1}** vs **{self.rapper2}** - {self.league} (`{self.length}`)"


class SongsHandler:
    songs: list[Song] = []
    up_next: list[Song] = []

    __choose_songs: list[Song] = []

    def __init__(self, folder: str, lookahead: int):
        with open(f"{folder}/meta.yml") as meta:
            songs = yaml.safe_load(meta.read())

        if len(songs) < lookahead:
            raise ValueError("lookahead too small: not enough songs to populate")

        for s in songs:
            song = Song(s["file"], s["rapper1"], s["rapper2"], s["league"], folder)
            self.songs.append(song)
        self.__choose_songs = self.songs.copy()

        self.choose(lookahead)

    def choose(self, count: int = 1):
        for _ in range(count):
            song = random.choice(self.__choose_songs)
            self.__choose_songs.remove(song)
            self.up_next.append(song)

    def next(self) -> Song:
        song = self.up_next.pop(0)
        self.__choose_songs.append(song)
        self.choose()

        return song
