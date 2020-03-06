from PIL import Image
from DDRDataTypes import DDRScreenshot, DDRParsedData
import sys, requests, io, os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: DDRGenie.py [path to screenshot image file]")
        exit(0)
    sshot = Image.open(sys.argv[1])
    if 'debug' in sys.argv:
        do_debug = True
    else:
        do_debug = False

    if 'upscale' in sys.argv:
        if not os.path.exists('deepai_key.txt'):
            print("To upscale you need to have a DeepAI API key in the working directory.\n"
                  " Make deepai_key.txt and save your key there and try again.")
            print("Skipping upscale...")
            mult = 1
        else:
            with open('deepai_key.txt', 'r') as f:
                apikey = f.read()
            mult = 2
            imgArr = io.BytesIO()
            sshot.save(imgArr, format='PNG')
            print("Uploading image to waifu2x cloud...")
            r = requests.post(
                "https://api.deepai.org/api/waifu2x",
                files={
                    'image': imgArr.getvalue(),
                },
                headers={'api-key': '%s' % apikey.strip()}
            )
            js = r.json()
            if do_debug:
                print(js)
            if 'output_url' in js:
                print("Downloading upscaled image...")
                r1 = requests.get(js['output_url'])
                reqdata = io.BytesIO(r1.content)
                sshot = Image.open(reqdata)
                if do_debug:
                    sshot.save("%s-2x.png" % sys.argv[1], format='PNG')
    else:
        mult = 1

    i = DDRScreenshot(sshot, size_multiplier=mult)

    d = DDRParsedData(i, debug=do_debug)
    print("%s|%s (C: %f)|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (d.dancer_name, d.song_title, d.title_conf, d.song_artist, d.play_letter_grade, d.play_money_score, d.play_max_combo,
                                                      d.play_ex_score, d.score_marv_count, d.score_perfect_count, d.score_great_count,
                                                      d.score_good_count, d.score_OK_count, d.score_miss_count, d.speed_mod, d.date_stamp,
                                                                          d.chart_difficulty, d.chart_play_mode, d.chart_difficulty_number))
