from PIL import Image
try:
    from .DDRSongListCorrector import DDRSongCorrector
except ImportError:
    from DDRSongListCorrector import DDRSongCorrector
import PIL
import PIL.ImageOps
import PIL.ImageFilter
import pytesseract


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

    # T/D
    date_stamp = None   # Good validation target!!!

    def __init__(self, base_image, size_multiplier=1):

        if not isinstance(base_image, PIL.Image.Image):
            raise Exception("base_image is not an image type!")
        self.size_multiplier = size_multiplier
        self.base_img = base_image
        self.crop_parts()

    def crop_parts(self):
        self.dancer_name = self.base_img.crop((440*self.size_multiplier, 6*self.size_multiplier, 580*self.size_multiplier, 37*self.size_multiplier))

        self.song_title = self.base_img.crop((148*self.size_multiplier, 33*self.size_multiplier, 577*self.size_multiplier, 58*self.size_multiplier))
        self.song_artist = self.base_img.crop((150*self.size_multiplier, 64*self.size_multiplier, 578*self.size_multiplier, 80*self.size_multiplier))

        self.chart_play_mode = self.base_img.crop((152*self.size_multiplier, 93*self.size_multiplier, 230*self.size_multiplier, 115*self.size_multiplier))
        self.chart_difficulty = self.base_img.crop((150*self.size_multiplier, 114*self.size_multiplier, 225*self.size_multiplier, 130*self.size_multiplier))
        self.chart_difficulty_number = self.base_img.crop((228*self.size_multiplier, 94*self.size_multiplier, 299*self.size_multiplier, 131*self.size_multiplier))

        self.play_grade = self.base_img.crop((70*self.size_multiplier, 165*self.size_multiplier, 189*self.size_multiplier, 242*self.size_multiplier))
        self.play_new_records = self.base_img.crop((220*self.size_multiplier, 136*self.size_multiplier, 357*self.size_multiplier, 161*self.size_multiplier))
        self.play_money_score = self.base_img.crop((218*self.size_multiplier, 164*self.size_multiplier, 365*self.size_multiplier, 192*self.size_multiplier))
        self.play_target_diff = self.base_img.crop((251*self.size_multiplier, 191*self.size_multiplier, 386*self.size_multiplier, 207*self.size_multiplier))
        self.play_max_combo = self.base_img.crop((322*self.size_multiplier, 208*self.size_multiplier, 372*self.size_multiplier, 230*self.size_multiplier))
        self.play_ex_score = self.base_img.crop((310*self.size_multiplier, 222*self.size_multiplier, 383*self.size_multiplier, 258*self.size_multiplier))

        self.score_marv_count = self.base_img.crop((152*self.size_multiplier, 266*self.size_multiplier, 206*self.size_multiplier, 280*self.size_multiplier))
        self.score_perfect_count = self.base_img.crop((152*self.size_multiplier, 282*self.size_multiplier, 206*self.size_multiplier, 305*self.size_multiplier))
        self.score_great_count = self.base_img.crop((152*self.size_multiplier, 304*self.size_multiplier, 206*self.size_multiplier, 326*self.size_multiplier))
        self.score_good_count = self.base_img.crop((152*self.size_multiplier, 323*self.size_multiplier, 206*self.size_multiplier, 343*self.size_multiplier))
        self.score_OK_count = self.base_img.crop((152*self.size_multiplier, 343*self.size_multiplier, 206*self.size_multiplier, 364*self.size_multiplier))
        self.score_miss_count = self.base_img.crop((152*self.size_multiplier, 364*self.size_multiplier, 206*self.size_multiplier, 382*self.size_multiplier))

        self.date_stamp = self.base_img.crop((420*self.size_multiplier, 373*self.size_multiplier, 542*self.size_multiplier, 400*self.size_multiplier))

    def debug_show(self):
        for attr in vars(self):
            i = getattr(self, attr)
            if isinstance(i, PIL.Image.Image):
                i.show()


class DDRPartData(object):
    value = None
    config = None
    parsed = False

    def __init__(self, config="", invert=False, sharpen=False, lang='eng'):
        self.config = config
        self.invert = invert
        self.sharpen = sharpen
        self.lang = lang
        self.i = None

    def parse_from(self, i):
        self.i = i
        if self.invert:
            i = PIL.ImageOps.invert(i)
        if self.sharpen:
            i = i.filter(PIL.ImageFilter.SHARPEN)
        self.value = pytesseract.image_to_string(i, lang=self.lang, config=self.config)
        self.parsed = True

    def redo(self):
        if self.i is not None:
            self.parse_from(self.i)

    def __str__(self):
        return self.value


class DDRParsedData(object):

    def __init__(self, ss, debug=False):
        self.debug = debug
        self.dancer_name = DDRPartData("--psm 8 --oem 3", True, lang="eng+jpn")

        self.song_title = DDRPartData("--psm 7", False, lang="eng+jpn")
        self.song_artist = DDRPartData("--psm 7", True, lang="eng+jpn")

        # Chart info
        self.chart_play_mode = DDRPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty = DDRPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty_number = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)

        # Play info
        # play_grade = None
        self.play_letter_grade = None
        self.play_full_combo = ''
        # play_new_records = None
        self.play_money_score = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        #self.play_target_diff = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=-+0123456789", True)
        self.play_max_combo = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.play_ex_score = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)

        # Score info
        self.score_marv_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, True)
        self.score_perfect_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, True)
        self.score_great_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, True)
        self.score_good_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, True)
        self.score_OK_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, True)
        self.score_miss_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, True)

        # T/D
        self.date_stamp = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)  # Good validation target!!!

        self.title_conf = -1

        if not isinstance(ss, DDRScreenshot):
            raise Exception("Not a DDR screenshot...")

        v = vars(self)
        for var in v:
            p = getattr(self, var)
            if isinstance(p, DDRPartData):
                p.parse_from(getattr(ss, var))

        self.validate()

    def __str__(self):
        outstr = []
        for attr in vars(self):
            outstr.append("%s: %s" % (attr, getattr(self, attr)))
        return '\n'.join(outstr)

    def validate(self):
        # Sometimes the dark 0, can trip it up. Since Scores < 100k are VERY unlikely we'll sanitize across just <1mil
        money_score = int(self.play_money_score.value.strip())
        if money_score > 1000000:
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
            self.play_letter_grade = "D? Unless you failed..."

        # EXScore Correction
        try:
            ocr_ex = int(self.play_ex_score.value)
        except:
            ocr_ex = -1
        calc_ex = ((int(self.score_marv_count.value) + int(self.score_OK_count.value)) * 3) + \
                  (int(self.score_perfect_count.value) * 2) + int(self.score_great_count.value)

        if ocr_ex != calc_ex:
            self.play_ex_score.value = "%s* [%s]" % (str(calc_ex), ocr_ex)

        # Sanitize mode / diff
        if 'ERS' in self.chart_play_mode.value:
            self.chart_play_mode.value = 'VERSUS'

        if 'SING' in self.chart_play_mode.value:
            self.chart_play_mode.value = 'SINGLE'

        if 'DOUB' in self.chart_play_mode.value:
            self.chart_play_mode.value = 'DOUBLES'

        if 'BEGI' in self.chart_difficulty.value:
            self.chart_difficulty.value = 'BEGINNER'

        if 'BASI' in self.chart_difficulty.value:
            self.chart_difficulty.value = 'BASIC'

        if 'DIFF' in self.chart_difficulty.value:
            self.chart_difficulty.value = 'DIFFICULT'

        if 'EXP' in self.chart_difficulty.value:
            self.chart_difficulty.value = 'EXPERT'

        if 'CHA' in self.chart_difficulty.value:
            self.chart_difficulty.value = 'CHALLENGE'

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

        # Title matching!
        if self.song_title.value == '':
            self.song_title.value = "Unknown"

        if self.debug:
            echo = True
        else:
            echo = False
        slc = DDRSongCorrector("a20_songlist.txt", echo=echo)
        eng_ratio, title, artist = slc.check_title(self.song_title.value)

        # Try and reparse...
        if eng_ratio < 0.40:
            self.song_title.lang = 'jpn'
            self.song_title.redo()
            self.song_artist.lang = 'jpn'
            self.song_artist.redo()
            jpn_ratio, jpn_title, jpn_artist = slc.check_title(self.song_title.value)
            if jpn_ratio < 0.34:
                self.song_title.value += '?'
                self.song_artist.value += '?'
                if jpn_ratio > eng_ratio:
                    self.title_conf = jpn_ratio
                else:
                    self.title_conf = eng_ratio
            elif jpn_ratio > eng_ratio:
                self.song_title.value = jpn_title
                self.song_artist.value = jpn_title
                self.title_conf = jpn_ratio
            else:
                self.song_title.value = title
                self.song_artist.value = artist
                self.title_conf = eng_ratio
        else:
            self.song_title.value = title
            self.song_artist.value = artist
            self.title_conf = eng_ratio
