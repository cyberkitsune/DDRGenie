from PIL import Image
from DDRDataTypes import DDRScreenshot, DDRParsedData
import sys

if __name__ == "__main__":
    if len(sys.argv < 2):
        print("Usage: DDRGenie.py [path to screenshot image file]")
        exit(0)
    sshot = Image.open(sys.argv[1])
    i = DDRScreenshot(sshot)
    d = DDRParsedData(i)
    print(d)

