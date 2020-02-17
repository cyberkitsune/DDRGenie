from PIL import Image
import PIL

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
    date_stamp = None # Good validation target!!!

    def __init__(self, base_image):
        if not isinstance(base_image, PIL.JpegImagePlugin.JpegImageFile):
            raise Exception("base_image is not an image type!")

        self.base_img = base_image
        self.crop_parts()

    def crop_parts(self):
        self.dancer_name = self.base_img.crop((442, 12, 570, 28))

        self.song_title = self.base_img.crop((148, 33, 577, 58))
        self.song_artist = self.base_img.crop((150, 64, 578, 80))

        self.chart_play_mode = self.base_img.crop((152, 93, 230, 115))
        self.chart_difficulty = self.base_img.crop((150, 114, 225, 130))
        self.chart_difficulty_number = self.base_img.crop((232, 94, 288, 132))

        self.play_grade = self.base_img.crop((70, 165, 189, 242))
        self.play_new_records = self.base_img.crop((220, 136, 357, 161))
        self.play_money_score = self.base_img.crop((218, 164, 365, 192))
        self.play_target_diff = self.base_img.crop((223, 191, 368, 209))
        self.play_max_combo = self.base_img.crop((322, 208, 372, 230))
        self.play_ex_score = self.base_img.crop((318, 228, 372, 250))

        self.score_marv_count = self.base_img.crop((152, 266, 206, 280))
        self.score_perfect_count = self.base_img.crop((152, 282, 206, 305))
        self.score_great_count = self.base_img.crop((152, 304, 206, 326))
        self.score_good_count = self.base_img.crop((152, 323, 206, 343))
        self.score_OK_count = self.base_img.crop((152, 343, 206, 364))
        self.score_miss_count = self.base_img.crop((152, 364, 206, 382))

        self.date_stamp = self.base_img.crop((420, 373, 542, 400))


