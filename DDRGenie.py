from PIL import Image
from DDRDataTypes import DDRScreenshot
import sys, PIL

if __name__ == "__main__":
    sshot = Image.open(sys.argv[1])
    i = DDRScreenshot(sshot)

    # Debug, let's view them all!
    for image_v in vars(i):
        if 'score_' not in image_v:
            continue
        img = getattr(i, image_v)
        if isinstance(img, PIL.Image.Image):
            print(image_v)
            img.show()
