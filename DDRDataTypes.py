from PIL import Image
import PIL
import PIL.ImageOps
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

    def __init__(self, base_image):
        if not isinstance(base_image, PIL.JpegImagePlugin.JpegImageFile):
            raise Exception("base_image is not an image type!")

        self.base_img = base_image
        self.crop_parts()

    def crop_parts(self):
        self.dancer_name = self.base_img.crop((440, 6, 580, 37))

        self.song_title = self.base_img.crop((148, 33, 577, 58))
        self.song_artist = self.base_img.crop((150, 64, 578, 80))

        self.chart_play_mode = self.base_img.crop((152, 93, 230, 115))
        self.chart_difficulty = self.base_img.crop((150, 114, 225, 130))
        self.chart_difficulty_number = self.base_img.crop((237, 86, 288, 136))

        self.play_grade = self.base_img.crop((70, 165, 189, 242))
        self.play_new_records = self.base_img.crop((220, 136, 357, 161))
        self.play_money_score = self.base_img.crop((218, 164, 365, 192))
        self.play_target_diff = self.base_img.crop((251, 191, 386, 207))
        self.play_max_combo = self.base_img.crop((322, 208, 372, 230))
        self.play_ex_score = self.base_img.crop((310, 222, 383, 258))

        self.score_marv_count = self.base_img.crop((152, 266, 206, 280))
        self.score_perfect_count = self.base_img.crop((152, 282, 206, 305))
        self.score_great_count = self.base_img.crop((152, 304, 206, 326))
        self.score_good_count = self.base_img.crop((152, 323, 206, 343))
        self.score_OK_count = self.base_img.crop((152, 343, 206, 364))
        self.score_miss_count = self.base_img.crop((152, 364, 206, 382))

        self.date_stamp = self.base_img.crop((420, 373, 542, 400))


class DDRPartData(object):
    value = None
    config = None
    parsed = False

    def __init__(self, config="", invert=False):
        self.config = config
        self.invert = invert

    def parse_from(self, i):
        if self.invert:
            i = PIL.ImageOps.invert(i)
        self.value = pytesseract.image_to_string(i, config=self.config)
        self.parsed = True

    def __str__(self):
        return self.value


class DDRParsedData(object):

    def __init__(self, ss):
        self.dancer_name = DDRPartData("--psm 8", True)

        self.song_title = DDRPartData("--psm 7")
        self.song_artist = DDRPartData("--psm 7", True)

        # Chart info
        self.chart_play_mode = DDRPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty = DDRPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty_number = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)

        # Play info
        # play_grade = None
        # play_new_records = None
        self.play_money_score = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        #self.play_target_diff = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=-+0123456789", True)
        self.play_max_combo = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.play_ex_score = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)

        # Score info
        self.score_marv_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.score_perfect_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.score_great_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.score_good_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.score_OK_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)
        self.score_miss_count = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)

        # T/D
        self.date_stamp = DDRPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True)  # Good validation target!!!

        self.letter_grade = None
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
        money_score = int(self.play_money_score.value)
        if money_score > 1000000:
            self.play_money_score.value = str(money_score - 1000000)

        # Generate letter grade (Ace Scoring)
        if money_score >= 990000:
            self.letter_grade = "AAA"
        elif money_score >= 950000:
            self.letter_grade = "AA+"
        elif money_score >= 900000:
            self.letter_grade = "AA"
        elif money_score >= 890000:
            self.letter_grade = "AA-"
        elif money_score >= 850000:
            self.letter_grade = "A+"
        elif money_score >= 800000:
            self.letter_grade = "A"
        elif money_score >= 790000:
            self.letter_grade = "A-"
        elif money_score >= 750000:
            self.letter_grade = "B+"
        elif money_score >= 700000:
            self.letter_grade = "B"
        elif money_score >= 690000:
            self.letter_grade = "B-"
        elif money_score >= 650000:
            self.letter_grade = "C+"
        elif money_score >= 600000:
            self.letter_grade = "C"
        elif money_score >= 590000:
            self.letter_grade = "C-"
        elif money_score >= 550000:
            self.letter_grade = "D+"
        elif money_score >= 500000:
            self.letter_grade = "D"
        else:
            self.letter_grade = "D? Unless you failed..."

        # EXScore Correction
        ocr_ex = int(self.play_ex_score.value)
        calc_ex = ((int(self.score_marv_count.value) + int(self.score_OK_count.value)) * 3) + \
                  (int(self.score_perfect_count.value) * 2) + int(self.score_great_count.value)

        if ocr_ex != calc_ex:
            self.play_ex_score.value = "%s* [%s]" % (str(calc_ex), ocr_ex)

        # Sanitize mode / diff
        if 'VERS' in self.chart_play_mode.value:
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

