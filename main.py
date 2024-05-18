import time
import keyboard
import mss
import numpy as np
from configs import *
from master_control import *
from detect_notes import *

# get config
successful_b, config = GetConfig(f_width_int=1920, 
                                 f_height_int=1080, 
                                 f_buttonNumber_int=4)
if not successful_b: 
    print("No config found")
    exit()

# initialize master
master = CMaster(config)

FPS = 60
CYCLE_TIME = (float)(1/FPS)
with mss.mss() as sct:
    # get correct monitor
    monitor = sct.monitors[2]

    # start when e pressed
    while True:
        if keyboard.is_pressed("e"): break

    while True:
        # quit when q pressed
        if keyboard.is_pressed("q"): break

        # get start time
        beginTimeSec_fl = time.time()
                
        # get screen shot
        screenshot_npa = np.array(sct.grab(monitor))

        # detect notes for each track
        tracks_lst = DetectNotesInTracks(config, screenshot_npa)

        # update master with new tracks information
        master.update(beginTimeSec_fl, tracks_lst)

        # update key status based on track information
        master.updateKey()

        # calculate consumed time and wait time according pre-defined fps
        # when consumed time is lower than defined cycle time, wait for the 
        # remaining cycle; otherwise head to next cycle directly
        endTimeSec_fl = time.time()
        elapsedTimeSec_fl = endTimeSec_fl - beginTimeSec_fl
        if elapsedTimeSec_fl < CYCLE_TIME: time.sleep(CYCLE_TIME-elapsedTimeSec_fl)
