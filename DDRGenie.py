from PIL import Image
from DDRDataTypes import DDRScreenshot, DDRParsedData
import sys, PIL

if __name__ == "__main__":
    sshot = Image.open(sys.argv[1])
    i = DDRScreenshot(sshot)
    #i.play_money_score.show()
    d = DDRParsedData(i)
    print(d)

