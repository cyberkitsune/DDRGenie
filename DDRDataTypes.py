from PIL import Image
try:
    from .DDRSongListCorrector import DDRSongCorrector
except ImportError:
    from DDRSongListCorrector import DDRSongCorrector
import PIL
import PIL.ImageOps
import PIL.ImageFilter
import pytesseract
import os
import datetime
from difflib import SequenceMatcher


def check_known_seq(check_string, valid_options, debug=False):
    if debug:
        print("Checking", check_string, "!")
    winner = (0, '')
    for option in valid_options:
        s_1 = check_string.lower().strip()
        s_2 = option.lower().strip()
        ratio = SequenceMatcher(a=s_1, b=s_2).ratio()
        if ratio > winner[0]:
            winner = (ratio, option)

    if debug:
        print("%s won at %f" % (winner[1].rstrip(), winner[0]))

    return winner[0], winner[1]


class DDRScreenshot(object):
    # Whole image
    base_img: Image = None

    # Player info
    dancer_name = None

    # Song meta
    # song_album_art = None
    song_title = None
    song_artist = None

    # Chart info
    chart_play_mode = None
    chart_difficulty = None
    chart_difficulty_number = None

    # Play info
    play_grade = None
    play_new_records = None
    play_money_score = None
    play_target_diff = None
    play_max_combo = None
    play_ex_score = None

    # Mods
    # TODO

    # Score info
    score_marv_count = None
    score_perfect_count = None
    score_great_count = None
    score_good_count = None
    score_OK_count = None
    score_miss_count = None

    speed_mod = None

    album_art = None

    # T/D
    date_stamp = None   # Good validation target!!!

    def __init__(self, base_image, size_multiplier=1):

        if not isinstance(base_image, PIL.Image.Image):
            raise Exception("base_image is not an image type!")
        self.size_multiplier = size_multiplier
        self.base_img = base_image
        self.crop_parts()

    def crop_parts(self):
        mult = self.size_multiplier
        self.dancer_name = self.base_img.crop((440*mult, 6*mult, 580*mult, 37*mult))

        self.song_title = self.base_img.crop((148*mult, 33*mult, 577*mult, 58*mult))
        self.song_artist = self.base_img.crop((150*mult, 64*mult, 578*mult, 80*mult))

        self.chart_play_mode = self.base_img.crop((160*mult, 95*mult, 239*mult, 112*mult))
        self.chart_difficulty = self.base_img.crop((160*mult, 113*mult, 239*mult, 130*mult))
        self.chart_difficulty_number = self.base_img.crop((228*mult, 94*mult, 286*mult, 131*mult))

        self.play_grade = self.base_img.crop((85*mult, 165*mult, 189*mult, 242*mult))
        self.play_new_records = self.base_img.crop((220*mult, 136*mult, 357*mult, 161*mult))
        self.play_money_score = self.base_img.crop((218*mult, 164*mult, 365*mult, 192*mult))
        self.play_target_diff = self.base_img.crop((251*mult, 191*mult, 386*mult, 207*mult))
        self.play_max_combo = self.base_img.crop((316*mult, 207*mult, 379*mult, 225*mult))
        self.play_ex_score = self.base_img.crop((315*mult, 227*mult, 378*mult, 245*mult))

        self.score_marv_count = self.base_img.crop((147*mult, 264*mult, 215*mult, 281*mult))
        self.score_perfect_count = self.base_img.crop((147*mult, 284*mult, 215*mult, 301*mult))
        self.score_great_count = self.base_img.crop((147*mult, 304*mult, 215*mult, 321*mult))
        self.score_good_count = self.base_img.crop((147*mult, 324*mult, 215*mult, 341*mult))
        self.score_OK_count = self.base_img.crop((147*mult, 344*mult, 215*mult, 361*mult))
        self.score_miss_count = self.base_img.crop((147*mult, 364*mult, 215*mult, 381*mult))

        self.speed_mod = self.base_img.crop((387*mult, 258*mult, 403*mult, 274*mult))

        self.date_stamp = self.base_img.crop((424*mult, 378*mult, 572*mult, 394*mult))

        self.album_art = self.base_img.crop((19*mult, 17*mult, 138*mult, 136*mult))

    def debug_show(self):
        for attr in vars(self):
            i = getattr(self, attr)
            if isinstance(i, PIL.Image.Image):
                print("Showing %s" % attr)
                i.show()


class DDRPartData(object):
    value = None
    config = None
    parsed = False

    def __init__(self, config="", invert=False, sharpen=False, lang='eng', pre_binarize=False):
        self.config = config
        self.invert = invert
        self.sharpen = sharpen
        self.lang = lang
        self.i = None
        self.orig_i = None
        self.pre_binarize = pre_binarize
        self.threshold = 100

    def parse_from(self, i):
        self.orig_i = i
        self.i = i
        if self.invert:
            self.i = PIL.ImageOps.invert(self.i)
        if self.sharpen:
            self.i = self.i.filter(PIL.ImageFilter.SHARPEN)
        if self.pre_binarize:
            # Binarize
            im2 = self.i.convert("L")
            self.i = im2.point(lambda p: p > self.threshold and 255)
        self.value = pytesseract.image_to_string(self.i, lang=self.lang, config=self.config)
        self.parsed = True

    def redo(self):
        if self.orig_i is not None:
            self.parse_from(self.orig_i)

    def debug_show(self):
        if self.i is not None:
            self.i.show()

    def __str__(self):
        return self.value


class DDRParsedData(object):

    def __init__(self, ss, debug=False):
        self.debug = debug
        self.dancer_name = DDRPartData("--psm 8 --oem 3", True, lang="eng+jpn", pre_binarize=True)

        self.song_title = DDRPartData("--psm 7", False, lang="eng+jpn", pre_binarize=True)
        self.song_artist = DDRPartData("--psm 7", True, lang="eng+jpn", pre_binarize=True)

        # Chart info
        self.chart_play_mode = DDRPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty = DDRPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty_number = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True)

        # Play info
        self.play_grade = DDRPartData("--psm 10 --oem 3", True, pre_binarize=True)
        self.play_letter_grade = None
        self.play_full_combo = ''
        # play_new_records = None
        self.play_money_score = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True)
        #self.play_target_diff = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=-+0123456789", True)
        self.play_max_combo = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True)
        self.play_ex_score = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True)

        # Score info
        self.score_marv_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, False, pre_binarize=True)
        self.score_perfect_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, False, pre_binarize=True)
        self.score_great_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, False, pre_binarize=True)
        self.score_good_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, False, pre_binarize=True)
        self.score_OK_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, False, pre_binarize=True)
        self.score_miss_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, False, pre_binarize=True)

        # Speedmod is not accurate yet...
        self.speed_mod = DDRPartData("--psm 7 --oem 3 -c tessedit_char_whitelist=123456789.xX", True, True)

        # T/D
        self.date_stamp = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True)  # Good validation target!!!

        self.title_conf = -1

        self.date_time = None

        self.bad_judge = False

        if not isinstance(ss, DDRScreenshot):
            raise Exception("Not a DDR screenshot...")

        v = vars(self)
        for var in v:
            p = getattr(self, var)
            if isinstance(p, DDRPartData):
                p.parse_from(getattr(ss, var))
                if debug:
                    p.debug_show()

        self.validate()

    def __str__(self):
        outstr = []
        for attr in vars(self):
            outstr.append("%s: %s" % (attr, getattr(self, attr)))
        return '\n'.join(outstr)

    def validate(self):
        # Sometimes the dark 0, can trip it up. Since Scores < 100k are VERY unlikely we'll sanitize across just <1mil
        money_score = int(self.play_money_score.value.strip())
        while money_score > 1000000:
            self.play_money_score.value = str(money_score - 1000000)
            money_score = money_score - 1000000

        # Generate letter grade (Ace Scoring)
        if money_score >= 990000:
            self.play_letter_grade = "AAA"
        elif money_score >= 950000:
            self.play_letter_grade = "AA+"
        elif money_score >= 900000:
            self.play_letter_grade = "AA"
        elif money_score >= 890000:
            self.play_letter_grade = "AA-"
        elif money_score >= 850000:
            self.play_letter_grade = "A+"
        elif money_score >= 800000:
            self.play_letter_grade = "A"
        elif money_score >= 790000:
            self.play_letter_grade = "A-"
        elif money_score >= 750000:
            self.play_letter_grade = "B+"
        elif money_score >= 700000:
            self.play_letter_grade = "B"
        elif money_score >= 690000:
            self.play_letter_grade = "B-"
        elif money_score >= 650000:
            self.play_letter_grade = "C+"
        elif money_score >= 600000:
            self.play_letter_grade = "C"
        elif money_score >= 590000:
            self.play_letter_grade = "C-"
        elif money_score >= 550000:
            self.play_letter_grade = "D+"
        elif money_score >= 500000:
            self.play_letter_grade = "D"
        else:
            self.play_letter_grade = "D / E?"

        if self.debug:
            print("LTR Grade: %s" % self.play_grade.value)
        if self.play_grade.value == 'E':
            self.play_letter_grade = "E"

        # EXScore Correction
        try:
            ocr_ex = int(self.play_ex_score.value)
        except:
            ocr_ex = -1

        # Judgement compromised?
        for attr in vars(self):
            if 'score_' in attr:
                j = getattr(self, attr)
                if len(j.value) > 4:
                    self.bad_judge = True

        if not self.bad_judge:
            calc_ex = ((int(self.score_marv_count.value) + int(self.score_OK_count.value)) * 3) + \
                      (int(self.score_perfect_count.value) * 2) + int(self.score_great_count.value)
        else:
            calc_ex = ocr_ex

        if ocr_ex != calc_ex:
            self.play_ex_score.value = "%s* [%s]" % (str(calc_ex), ocr_ex)

        # Correct difficulty and mode
        mode_conf, new_mode = check_known_seq(self.chart_play_mode.value, ['VERSUS', 'SINGLE', 'DOUBLE'])

        diff_conf, new_diff = check_known_seq(self.chart_difficulty.value, ['BEGINNER', 'BASIC', 'DIFFICULT', 'EXPERT', 'CHALLENGE'])

        if mode_conf > 0.40:
            self.chart_play_mode.value = new_mode
        else:
            # I've only ever encountered this on gold cab versus. The contrast of versus fucks with the OCR a lot.
            # Considering the statistics I think it's safe to default to single (versus is considered single anyway...)
            self.chart_play_mode.value = 'SINGLE'

        if diff_conf > 0.40:
            self.chart_difficulty.value = new_diff

        # FC Calc
        if int(self.score_miss_count.value) == 0:
            if int(self.score_good_count.value) > 0:
                self.play_full_combo = "FC "
            elif int(self.score_great_count.value) > 0:
                self.play_full_combo = "GFC! "
            elif int(self.score_perfect_count.value) > 0:
                self.play_full_combo = "PFC!! "
            elif int(self.score_marv_count.value) > 0:
                self.play_full_combo = "MFC!!! "
        else:
            self.play_full_combo = ""

        # Clean pipes
        self.dancer_name.value = self.dancer_name.value.strip('|')

        # Time formatting
        self.date_stamp.value = self.date_stamp.value.replace(" ", "")
        if len(self.date_stamp.value) != 12:
            self.date_stamp.value = "Unknown (Parsed: %s)" % self.date_stamp.value
        else:
            year = ''.join(self.date_stamp.value[0:4])
            month = ''.join(self.date_stamp.value[4:6])
            day = ''.join(self.date_stamp.value[6:8])
            hh = ''.join(self.date_stamp.value[8:10])
            mm = ''.join(self.date_stamp.value[10:12])
            self.date_stamp.value = "%s.%s.%s %s:%s" % (year, month, day, hh, mm)
            self.date_time = datetime.datetime(int(year), int(month), int(day), int(hh), int(mm))
            self.date_time = self.date_time - datetime.timedelta(hours=9)

        if self.debug:
            echo = True
        else:
            echo = False
        folder = os.path.dirname(__file__)
        slc = DDRSongCorrector("%s/genie_assets/a20_songlist.txt" % folder, echo=echo)
        eng_ratio, title, artist = slc.check_title(self.song_title.value, self.song_artist.value)

        # Try and reparse...
        if eng_ratio < 0.40:
            self.song_title.lang = 'jpn'
            self.song_title.redo()
            self.song_artist.lang = 'jpn'
            self.song_artist.redo()
            jpn_ratio, jpn_title, jpn_artist = slc.check_title(self.song_title.value, self.song_artist.value)
            if jpn_ratio < 0.34:
                self.song_title.value += '?'
                self.song_artist.value += '?'
                if jpn_ratio > eng_ratio:
                    self.title_conf = jpn_ratio
                else:
                    self.title_conf = eng_ratio
            elif jpn_ratio > eng_ratio:
                self.song_title.value = jpn_title
                self.song_artist.value = jpn_artist
                self.title_conf = jpn_ratio
            else:
                self.song_title.value = title
                self.song_artist.value = artist
                self.title_conf = eng_ratio
        else:
            self.song_title.value = title
            self.song_artist.value = artist
            self.title_conf = eng_ratio
