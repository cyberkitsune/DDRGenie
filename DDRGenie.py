from PIL import Image
from DDRDataTypes import DDRScreenshot, DDRParsedData
import sys, PIL

if __name__ == "__main__":
    sshot = Image.open(sys.argv[1])
    i = DDRScreenshot(sshot)
    i.chart_difficulty_number.show()
    #i.play_ex_score.show()
    #i.dancer_name.show()
    #i.play_target_diff.show()
    #i.score_great_count.show()
    #i.play_target_diff.show()

    #i.dancer_name.show()

    #i.song_artist.show()

    #i.chart_difficulty_number.show()
    #i.chart_difficulty_number.show()
    d = DDRParsedData(i)
    print(d)

