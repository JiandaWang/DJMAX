from configs import *
from master import *
import mss
import time
import keyboard
import numpy as np
from copy import deepcopy
import pickle

# initialize master
master = CMaster()
# initialize debug buffer
debugBuffer = []

with mss.mss() as sct:
    # get correct monitor
    monitor = sct.monitors[2]
    # outmost while loop
    quitProgram_b = False
    while not quitProgram_b:
        # start when e pressed
        while not quitProgram_b:
            if keyboard.is_pressed("e"): break
            # quit when q pressed
            if keyboard.is_pressed("q"):
                # set quit program to true
                quitProgram_b = True
                break
        while not quitProgram_b:
            # reset when r pressed
            if keyboard.is_pressed("r"):            
                # del and re-create master
                del master
                master = CMaster()
                break
            # quit when q pressed
            if keyboard.is_pressed("q"):
                # set quit program to true
                quitProgram_b = True
                break
            # get start time
            beginTimeSec_fl = time.time()
            # get screen shot and frame
            screenshot_npa = np.array(sct.grab(monitor))
            master.getFrame(screenshot_npa)
            # detect notes
            master.detectLines()
            # update time, speed, prediction
            master.updateTimeSpeedPrediction(beginTimeSec_fl)
            # detect key action
            master.decideKeyAction()
            # press key
            master.pressKey()
            # save debug information
            if DEBUG:
                debugBuffer.append(deepcopy(master))
                if len(debugBuffer) > MAX_DEBUG_CYCLE: debugBuffer.pop(0)
            # update previous buffer for next cycle
            master.updatePrevBufferForNextCycle()
            # calculate consumed time and wait time according pre-defined fps
            # when consumed time is lower than defined cycle time, wait for the
            # remaining cycle; otherwise head to next cycle directly
            endTimeSec_fl = time.time()
            elapsedTimeSec_fl = endTimeSec_fl - beginTimeSec_fl
            if elapsedTimeSec_fl < CYCLE_TIME: time.sleep(CYCLE_TIME-elapsedTimeSec_fl)

# do the clean
master.clean()
# save to pickle file
if DEBUG:
    with open("debugBuffer.pkl", 'wb') as f:
        pickle.dump(debugBuffer, f)
