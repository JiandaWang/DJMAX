class CConfig():
    def __init__(self, 
                 f_judgeLinePosY_int = 0,
                 f_noteDetectionLinePosY_int = 0,
                 f_trackWidth_int = 0,
                 f_noteHeight_int = 0,
                 f_keyToTrackPosXs_dict = {}):
        self.m_judgeLinePosY_int = f_judgeLinePosY_int
        self.m_noteDetectionLinePosY_int = f_noteDetectionLinePosY_int
        self.m_trackWidth_int = f_trackWidth_int
        self.m_noteHeight_int = f_noteHeight_int
        self.m_keyToTrackPosXs_dict = f_keyToTrackPosXs_dict

CONFIGS = {
    "1920W_1080H_4B": CConfig(f_judgeLinePosY_int = 765,
                              f_noteDetectionLinePosY_int = 590,
                              f_trackWidth_int = 120,
                              f_noteHeight_int = 28,
                              f_keyToTrackPosXs_dict = {"a": 720, 
                                                        "s": 840, 
                                                        ";": 960, 
                                                        "\'": 1080
                                                       }),
    "1920W_1080H_5B": CConfig(f_judgeLinePosY_int = 765,
                              f_noteDetectionLinePosY_int = 590,
                              f_trackWidth_int = 96,
                              f_noteHeight_int = 28,
                              f_keyToTrackPosXs_dict = {"a": 720, 
                                                        "s": 816,
                                                        "c": 912,
                                                        ";": 1008,
                                                        "\'": 1104
                                                       }),
    "1920W_1080H_6B": CConfig(f_judgeLinePosY_int = 765,
                              f_noteDetectionLinePosY_int = 590,
                              f_trackWidth_int = 80,
                              f_noteHeight_int = 28,
                              f_keyToTrackPosXs_dict = {"a": 720, 
                                                        "s": 800,
                                                        "c": 880,
                                                        ",": 960,
                                                        ";": 1040,
                                                        "\'": 1120
                                                       })
}

def GetConfig(f_width_int, f_height_int, f_buttonNumber_int):
    # get the correspoding config name
    configName_str = str(f_width_int) + "W_" \
                    +str(f_height_int) + "H_" \
                    +str(f_buttonNumber_int) + "B"
    
    # get config based on config name; if not available return not successful
    if configName_str in CONFIGS: return True, CONFIGS[configName_str]
    else: return False, []
