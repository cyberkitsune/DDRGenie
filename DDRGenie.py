from PIL import Image
from DDRDataTypes import DDRScreenshot, DDRParsedData
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: DDRGenie.py [path to screenshot image file]")
        exit(0)
    sshot = Image.open(sys.argv[1])
    i = DDRScreenshot(sshot)
    d = DDRParsedData(i)
    print("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (d.dancer_name, d.song_title, d.song_artist, d.play_letter_grade, d.play_money_score, d.play_max_combo,
                                                      d.play_ex_score, d.score_marv_count, d.score_perfect_count, d.score_great_count,
                                                      d.score_good_count, d.score_OK_count, d.score_miss_count))

