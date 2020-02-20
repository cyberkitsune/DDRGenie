from difflib import SequenceMatcher


class DDRSongCorrector(object):

    def __init__(self, songfile, echo=False):
        self.songs = []
        self.echo = echo
        with open(songfile, 'r') as f:
            for line in f.readlines():
                self.songs.append(tuple(line.split("/")))
        if self.echo:
            print("[SLC] Loaded %i songs!" % len(self.songs))

    def debug(self):
        for song in self.songs:
            print(song)

    def check_title(self, title):
        winner = (0, None)
        for song in self.songs:
            s_1 = title
            s_2 = song[0]
            ratio = SequenceMatcher(a=s_1, b=s_2).ratio()
            if ratio > winner[0]:
                winner = (ratio, song)

        if self.echo:
            print("%s - %s won at %f" % (winner[1][0], winner[1][1], winner[0]))

        return winner[0], winner[1][0], winner[1][1]

    def dump_ratios(self, title):
        ratios = []
        for song in self.songs:
            s_1 = title
            s_2 = song[0]
            ratio = SequenceMatcher(a=s_1, b=s_2).ratio()
            ratios.append((ratio, song))

        return ratios

