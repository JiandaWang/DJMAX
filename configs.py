class CSpeficic():
    def __init__(self,
                 f_judgeLinePosY_int,
                 f_noteDetectionLinePosY_int,
                 f_keyActionLinePosY_int,
                 f_leftEdge_int,
                 f_rightEdge_int,
                 f_trackWidth_int,
                 f_noteHeight_int,
                 f_trackPosXs_dict,
                 f_keyConfig_dict,
                 f_specialKeyMapping_dict):
        self.m_judgeLinePosY_int = f_judgeLinePosY_int
        self.m_noteDetectionLinePosY_int = f_noteDetectionLinePosY_int
        self.m_keyActionLinePosY_int = f_keyActionLinePosY_int
        self.m_leftEdge_int = f_leftEdge_int
        self.m_rightEdge_Int = f_rightEdge_int
        self.m_trackWidth_int = f_trackWidth_int
        self.m_noteHeight_int = f_noteHeight_int
        self.m_trackPosXs_dict = f_trackPosXs_dict
        self.m_keyConfig_dict = f_keyConfig_dict
        self.m_specialKeyMapping_dict = f_specialKeyMapping_dict



#################### CONFIG VALUES STARTS HERE ####################
# debug flag
DEBUG = False
# max cycle number for debug buffer
MAX_DEBUG_CYCLE = 60

# frame per second, indicates how often the frame would be processed
FPS = 30
CYCLE_TIME = (float)(1/FPS)

# thresholds for binary conversion + canny edge detection
CANNY_LOW_THRESH = 200
CANNY_HIGH_THRESH = 300

# overflow handling for speed buffer
MAX_ELAPSED_PIXEL = 100000
MAX_ELAPSED_TIME_SEC = 250

# thresholds for color classification
COLOR_PICK_OFFSET = 10
BGR_BLACK = [40, 40, 40]
BGR_WHITE = [180, 180, 180]
BGR_ORANGE = [80, 160, 220]
BGR_BLUE = [180, 180, 80]
BGR_RED = [60, 160, 20, 200]
COLOR_LAYER = {"black": 0, "blue": 1, "red": 1, "white": 2, "orange": 2}

# thresholds for key activation
COOLDOWN = 0.01 # avoid duplicated triggering within cooldown time

# variant
VARIANT = "1920W_1080H_6B8B"

# variant specific configs
KEY_CONFIG_4B = {"track1": "a", "track2": "s", "track3": ";", "track4": "\'", "side left": "left shift", "side right": "right shift"}
KEY_CONFIG_5B = {"track1": "a", "track2": "s", "track3": "c", "track4": ";", "track5": "\'", "side left": "left shift", "side right": "right shift"}
KEY_CONFIG_6B8B = {"track1": "a", "track2": "s", "track3": "c", "track4": ",", "track5": ";", "track6": "\'", "side left": "left shift", "side right": "right shift", "left": "left alt", "right": "space"}

SPECIAL_KEY_MAPPING_4B = {"track1": ("side left",),
                          "track2": ("side left",),
                          "track3": ("side right",),
                          "track4": ("side right",)
                         }
SPECIAL_KEY_MAPPING_5B = {"track1": ("side left",),
                          "track2": ("side left",),
                          "track3": (),
                          "track4": ("side right",),
                          "track5": ("side right",)
                         }
SPECIAL_KEY_MAPPING_6B8B = {"track1": ("side left", "left"),
                            "track2": ("side left", "left"),
                            "track3": ("side left", "left"),
                            "track4": ("side right", "right"),
                            "track5": ("side right", "right"),
                            "track6": ("side right", "right")
                           }

SPECIFICS = {
    "1920W_1080H_4B": CSpeficic(f_judgeLinePosY_int = 765,
                                f_noteDetectionLinePosY_int = 550,
                                f_keyActionLinePosY_int = 450,
                                f_leftEdge_int = 720,
                                f_rightEdge_int = 1200,
                                f_trackWidth_int = 120,
                                f_noteHeight_int = 20,
                                f_trackPosXs_dict = {"track1": 720, "track2": 840, "track3": 960, "track4": 1080},
                                f_keyConfig_dict = KEY_CONFIG_4B,
                                f_specialKeyMapping_dict = SPECIAL_KEY_MAPPING_4B
                               ),

    "1920W_1080H_5B": CSpeficic(f_judgeLinePosY_int = 765,
                                f_noteDetectionLinePosY_int = 550,
                                f_keyActionLinePosY_int = 450,
                                f_leftEdge_int = 720,
                                f_rightEdge_int = 1200,
                                f_trackWidth_int = 96,
                                f_noteHeight_int = 20,
                                f_trackPosXs_dict = {"track1": 720, "track2": 816, "track3": 912, "track4": 1008, "track5": 1104},
                                f_keyConfig_dict = KEY_CONFIG_5B,
                                f_specialKeyMapping_dict = SPECIAL_KEY_MAPPING_5B
                               ),

    "1920W_1080H_6B8B": CSpeficic(f_judgeLinePosY_int = 765,
                                  f_noteDetectionLinePosY_int = 550,
                                  f_keyActionLinePosY_int = 450,
                                  f_leftEdge_int = 720,
                                  f_rightEdge_int = 1200,
                                  f_trackWidth_int = 80,
                                  f_noteHeight_int = 20,
                                  f_trackPosXs_dict = {"track1": 720, "track2": 800, "track3": 880, "track4": 960, "track5": 1040, "track6": 1120},
                                  f_keyConfig_dict = KEY_CONFIG_6B8B,
                                  f_specialKeyMapping_dict = SPECIAL_KEY_MAPPING_6B8B
                                 )                                
}

##################### DERIVED CONFIG VALUES #####################
JUDGE_LINE_POS_Y = SPECIFICS[VARIANT].m_judgeLinePosY_int
NOTE_DETECT_END_LINE_POS_Y = SPECIFICS[VARIANT].m_noteDetectionLinePosY_int
NOTE_DETECT_START_LINE_POS_Y = SPECIFICS[VARIANT].m_noteHeight_int + COLOR_PICK_OFFSET*2
KEY_ACTION_LINE_POS_Y = SPECIFICS[VARIANT].m_keyActionLinePosY_int
LEFT_EDGE = SPECIFICS[VARIANT].m_leftEdge_int
RIGHT_EDGE = SPECIFICS[VARIANT].m_rightEdge_Int
TRACK_WIDTH = SPECIFICS[VARIANT].m_trackWidth_int
NOTE_HEIGHT = SPECIFICS[VARIANT].m_noteHeight_int
NOTE_HEIGHT_TOL = int(NOTE_HEIGHT*1.5)
TRACK_POS_X = SPECIFICS[VARIANT].m_trackPosXs_dict
KEY_CONFIG = SPECIFICS[VARIANT].m_keyConfig_dict
SPECIAL_KEY_MAPPING = SPECIFICS[VARIANT].m_specialKeyMapping_dict
HOUGH_THRESHOLD = int(TRACK_WIDTH/4)
HOUGH_MIN_LENGTH = int(TRACK_WIDTH/2)
HOUGH_MAX_GAP = int(TRACK_WIDTH/4)
HOUGH_HORIZONTAL_LINE_Y_DIFF = int(NOTE_HEIGHT/4)
LINE_MATCH_THRESHOLD = int(NOTE_HEIGHT/2)
