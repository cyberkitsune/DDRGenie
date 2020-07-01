from PIL import Image
import PIL
import PIL.ImageOps
import PIL.ImageFilter
import pytesseract
import os
import datetime
from difflib import SequenceMatcher
try:
    from .SongListCorrector import SongListCorrector
except ImportError:
    from SongListCorrector import SongListCorrector


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


class IIDXScreenshot(object):
    # Whole image
    base_img: Image = None

    # Player info
    dj_name = None

    # Song meta
    # song_album_art = None
    song_title = None
    song_artist = None

    # Chart info
    chart_play_mode = None
    chart_difficulty = None

    # Play info
    play_clear_type = None
    play_dj_level = None
    play_ex_score = None
    play_miss_count = None

    # Score info
    score_rainbow_count = None
    score_great_count = None
    score_good_count = None
    score_bad_count = None
    score_poor_count = None

    tracker_target = None
    tracker_value = None

    score_combo_break = None

    score_fast_count = None
    score_slow_count = None

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
        # Player info
        self.dj_name = self.base_img.crop((260*mult, 14*mult, 381*mult, 34*mult))

        self.song_title = self.base_img.crop((17*mult, 150*mult, 382*mult, 171*mult))
        self.song_artist = self.base_img.crop((17*mult, 174*mult, 382*mult, 191*mult))

        self.chart_play_mode = self.base_img.crop((19*mult, 129*mult, 43*mult, 146*mult))
        self.chart_difficulty = self.base_img.crop((49*mult, 131*mult, 117*mult, 144*mult))

        self.play_clear_type = self.base_img.crop((203*mult, 223*mult, 276*mult, 246*mult))
        self.play_dj_level = self.base_img.crop((203*mult, 251*mult, 274*mult, 273*mult))
        self.play_ex_score = self.base_img.crop((203*mult, 279*mult, 276*mult, 301*mult))
        self.play_miss_count = self.base_img.crop((203*mult, 307*mult, 276*mult, 329*mult))

        self.tracker_target = self.base_img.crop((17*mult, 359*mult, 201*mult, 385*mult))
        self.tracker_value = self.base_img.crop((203*mult, 362*mult, 276*mult, 384*mult))

        self.score_rainbow_count = self.base_img.crop((126*mult, 398*mult, 198*mult, 417*mult))
        self.score_great_count = self.base_img.crop((126*mult, 420*mult, 198*mult, 440*mult)) # + ,23
        self.score_good_count = self.base_img.crop((126*mult, 444*mult, 198*mult, 463*mult))
        self.score_bad_count = self.base_img.crop((126*mult, 467*mult, 198*mult, 486*mult))
        self.score_poor_count = self.base_img.crop((126*mult, 490*mult, 198*mult, 509*mult))

        self.score_combo_break = self.base_img.crop((128*mult, 515*mult, 198*mult, 534*mult))

        self.score_fast_count = self.base_img.crop((126*mult, 540*mult, 198*mult, 559*mult))
        self.score_slow_count = self.base_img.crop((126*mult, 563*mult, 198*mult, 582*mult))

        self.date_stamp = self.base_img.crop((12*mult, 14*mult, 153*mult, 38*mult))  # Good validation target!!!

    def debug_show(self):
        for attr in vars(self):
            i = getattr(self, attr)
            if isinstance(i, PIL.Image.Image):
                print("Showing %s" % attr)
                i.show()


class IIDXPartData(object):
    value = None
    config = None
    parsed = False

    def __init__(self, config="", invert=False, sharpen=False, lang='eng', pre_binarize=False, rescale=None, erode=0):
        self.config = config
        self.invert = invert
        self.sharpen = sharpen
        self.lang = lang
        self.i = None
        self.orig_i = None
        self.pre_binarize = pre_binarize
        self.threshold = 210
        self.rescale = rescale
        self.erode = erode

        if lang == 'iidx' or lang == 'iidx-grade' or lang == 'iidx-clr':
            folder = os.path.dirname(os.path.realpath(__file__))
            self.config = self.config + " --tessdata-dir \"%s/genie_assets/\"" % folder

    def parse_from(self, i):
        self.orig_i = i
        self.i = i
        if self.rescale is not None:
            self.i = i.resize((self.i.width * self.rescale[0], self.i.height * self.rescale[1]))
        if self.invert:
            self.i = PIL.ImageOps.invert(self.i)
        if self.sharpen:
            self.i = self.i.filter(PIL.ImageFilter.SHARPEN)
        if self.pre_binarize:
            # Binarize
            im2 = self.i.convert("L")
            self.i = im2.point(lambda p: p > self.threshold and 255)
        if self.erode > 0:
            self.i = self.i.filter(PIL.ImageFilter.MaxFilter(self.erode))
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


class IIDXParsedData(object):

    def __init__(self, ss, debug=False):
        self.debug = debug
        self.dj_name = IIDXPartData("--psm 8 --oem 3", True, lang="eng+jpn", pre_binarize=True)

        self.song_title = IIDXPartData("--psm 7", True, lang="eng+jpn", pre_binarize=True)
        self.song_artist = IIDXPartData("--psm 7", True, lang="eng+jpn", pre_binarize=True)

        self.chart_play_mode = IIDXPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True)
        self.chart_difficulty = IIDXPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True, pre_binarize=False)
        self.chart_difficulty.threshold = 115

        self.play_clear_type = IIDXPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True, pre_binarize=True, lang='iidx-clr+eng')
        self.play_dj_level = IIDXPartData("--psm 8 --oem 3 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ", True, pre_binarize=True, lang='iidx-grade')
        self.play_ex_score = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')
        self.play_miss_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')

        self.tracker_target = IIDXPartData("--psm 7", True, lang="eng+jpn", pre_binarize=True)
        self.tracker_value = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')

        self.score_rainbow_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')
        self.score_great_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')
        self.score_good_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')
        self.score_bad_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')
        self.score_poor_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')

        self.score_combo_break = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')

        self.score_fast_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')
        self.score_slow_count = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789", True, pre_binarize=True, lang='iidx')

        self.date_stamp = IIDXPartData("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789-", True, pre_binarize=True)

        self.date_time = None
        self.title_conf = None
        self.overall_conf = 0

        if not isinstance(ss, IIDXScreenshot):
            raise Exception("Not a IIDX screenshot...")

        v = vars(self)
        for var in v:
            p = getattr(self, var)
            if isinstance(p, IIDXPartData):
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

        # Correct difficulty and mode
        mode_conf, new_mode = check_known_seq(self.chart_play_mode.value, ['SP', 'DP'])

        diff_conf, new_diff = check_known_seq(self.chart_difficulty.value, ['BEGINNER', 'NORMAL', 'HYPER', 'ANOTHER'])

        self.play_clear_type.value.replace('€', 'E')

        clr_conf, new_clr = check_known_seq(self.play_clear_type.value, ['NO PLAY', 'FAILED', 'CLEAR', 'E-CLEAR', 'A-CLEAR',
                                                                         'H-CLEAR', 'EXH-CLEAR', 'F-COMBO'])

        grade_conf, new_grade = check_known_seq(self.play_dj_level.value, ['E', 'F', 'D', 'C', 'B', 'A', 'AA', 'AAA'])

        if mode_conf > 0.40:
            self.chart_play_mode.value = new_mode
        else:
            self.chart_play_mode.value = 'SP'

        if diff_conf > 0.40:
            self.chart_difficulty.value = new_diff

        if clr_conf > 0.40:
            self.play_clear_type.value = new_clr

        if grade_conf > 0.40:
            self.play_dj_level.value = new_grade

        # Time formatting
        self.date_stamp.value = self.date_stamp.value.replace(" ", "")
        self.date_stamp.value = self.date_stamp.value.replace("-", "")
        self.date_stamp.value = self.date_stamp.value.replace(".", "")
        self.date_stamp.value = self.date_stamp.value.replace(":", "")
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
        slc = SongListCorrector("%s/genie_assets/iidx_songlist.txt" % folder, echo=echo)
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

        self.overall_conf = ((self.title_conf * 100) + (grade_conf * 100) + (clr_conf * 100) + (diff_conf * 100) +
                             (mode_conf * 100)) / 5

