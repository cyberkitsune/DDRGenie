from difflib import SequenceMatcher
import json as js


class SongListCorrector(object):

    def __init__(self, songfile, echo=False, json=False):
        self.songs = []
        self.echo = echo

        with open(songfile, 'r') as f:
            if json:
                js_data = js.load(f)
                for song_entry in js_data:
                    self.songs.append((song_entry['song_title'], song_entry['artist']))
            else:
                for line in f.readlines():
                    self.songs.append(tuple(line.strip('\n').split(" / ")))
        if self.echo:
            print("[SLC] Loaded %i songs!" % len(self.songs))

    def debug(self):
        for song in self.songs:
            print(song)

    def check_title(self, title, artist):
        if self.echo:
            print("Checking", title, "!")
        winner = (0, ('', ''))
        for song in self.songs:
            s_1 = "%s %s" % (title.lower().strip(), artist.lower().strip())
            s_2 = "%s %s" % (song[0].lower().strip(), song[1].lower().strip())
            ratio = SequenceMatcher(a=s_1, b=s_2).ratio()
            if ratio > winner[0]:
                winner = (ratio, song)

        if self.echo:
            print("%s - %s won at %f" % (winner[1][0].rstrip(), winner[1][1].rstrip(), winner[0]))

        return winner[0], winner[1][0].rstrip(), winner[1][1].rstrip()

    def dump_ratios(self, title, artist):
        ratios = []
        for song in self.songs:
            s_1 = "%s %s" % (title.lower().strip(), artist.lower().strip())
            s_2 = "%s %s" % (song[0].lower().strip(), song[1].lower().strip())
            ratio = SequenceMatcher(a=s_1, b=s_2).ratio()
            ratios.append((ratio, song))

        return ratios

