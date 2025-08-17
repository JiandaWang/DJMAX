from configs import *
import cv2
import numpy as np
from copy import deepcopy
import time
import keyboard
import threading

class CMaster():
    def __init__(self):
        # frame information for current cycle and debug
        self.m_curColorFrame = []
        self.m_curGrayFrame = []
        self.m_prevColorFrame = []
        self.m_prevGrayFrame = []

        # detected lines
        self.m_curDetectedLines_dict = {}
        self.m_prevDetectedLines_dict = {}
        self.m_linePredictions_dict = {}

        # time stamp of last update
        self.m_curTimeStampSec_fl = 0
        self.m_prevTimeStampSec_fl = 0

        # save elapsed pixels and time for note falling speed estimation
        self.m_elapsedPixel_int = int(0)
        self.m_elapsedTimeSec_fl = 0

        # key actions
        self.m_curKeyActions_dict = {}
        self.m_keyTiming_dict = {}
        for track, key in KEY_CONFIG.items():
            self.m_keyTiming_dict[track] = [] # initialization necessary
            keyboard.release(key) # make sure all keys are released

    def getFrame(self, f_screenshot_npa):
        # crop the frame
        self.m_curColorFrame = f_screenshot_npa[0:JUDGE_LINE_POS_Y, LEFT_EDGE:RIGHT_EDGE]
        # convert to gray frame
        self.m_curGrayFrame = cv2.cvtColor(self.m_curColorFrame, cv2.COLOR_BGR2GRAY)

    def detectLines(self):
        for track, leftPos in TRACK_POS_X.items():
            # reset
            self.m_curDetectedLines_dict[track] = []
            # get the cropped frame
            croppedFrame = self.m_curGrayFrame[NOTE_DETECT_START_LINE_POS_Y:NOTE_DETECT_END_LINE_POS_Y, leftPos-LEFT_EDGE:leftPos-LEFT_EDGE+TRACK_WIDTH]
            # run canny
            edges = cv2.Canny(croppedFrame, CANNY_LOW_THRESH, CANNY_HIGH_THRESH)
            # apply hough transformation to find line
            # thresholds depend on track width so that they can automatically adjusted
            lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                    threshold=HOUGH_THRESHOLD,
                                    minLineLength=HOUGH_MIN_LENGTH,
                                    maxLineGap=HOUGH_MAX_GAP)

            # iterate over contours and find horizontal lines
            if not lines is None:
                for line in lines:
                    # get the coordinates
                    _, y1, _, y2 = line[0]
                    # check if horizontal -> if yes, output the average posY + offset for start line
                    if abs(y2 - y1) <= HOUGH_HORIZONTAL_LINE_Y_DIFF: self.m_curDetectedLines_dict[track].append(int((y1+y2)/2)+NOTE_DETECT_START_LINE_POS_Y)
                # sort the current detected lines
                self.m_curDetectedLines_dict[track].sort(reverse=True)

    def updateTimeSpeedPrediction(self, f_curTimeSec_fl):
        # save the current time stamp
        self.m_curTimeStampSec_fl = f_curTimeSec_fl
        # no need to check whether lines are detected, handled automatically      
        # in case speed not available, no prediction based on previous position possible
        # only do rough speed update based on detected line order
        if not self.__speedAvailable_b(): self.__updateWithoutSpeed()
        else: self.__updateWithSpeed()

    def decideKeyAction(self):
        # only proceed with speed already available
        if not self.__speedAvailable_b(): return
        # initialize key actions
        for track in KEY_CONFIG.keys(): self.m_curKeyActions_dict[track] = []
        # get speed
        speed_fl = float(self.m_elapsedPixel_int) / self.m_elapsedTimeSec_fl
        # loop over all current detected lines
        # for the part lower than KEY_ACTION_LINE_POS_Y, decide key action
        for track, lines in self.m_curDetectedLines_dict.items():
            index = 0
            while index < len(lines) and lines[index] > KEY_ACTION_LINE_POS_Y:
                # get line
                line = lines[index]
                # get the delay
                delay_fl = (JUDGE_LINE_POS_Y - line) / speed_fl
                # get classfication
                type_str, endTrack_str, startTrack_str = self.__classifyLine(line, track)
                # if end line, add release action
                if type_str == "end" or type_str == "both":
                    self.m_curKeyActions_dict[endTrack_str].append(("release", delay_fl))
                # if start line, depends on the color, check whether it's click or press
                if type_str == "start" or type_str == "both":
                    if self.__classifyLine(line-NOTE_HEIGHT, track)[0] == "end":
                        # upper line is and "end", it has to be a click
                        # but only trigger when not duplicated
                        if not self.__checkDuplication(startTrack_str, delay_fl):
                            self.m_curKeyActions_dict[startTrack_str].append(("click", delay_fl))
                            self.m_keyTiming_dict[startTrack_str].append(self.m_curTimeStampSec_fl + delay_fl)
                        # ignore everything within one note height
                        # notice there is one extra index += 1 at the end
                        while index < (len(lines)-1) and lines[index+1] >= line - NOTE_HEIGHT_TOL: index += 1
                    elif not self.__checkDuplication(startTrack_str, delay_fl): 
                        # long key activation, use press, when not duplicated
                        self.m_curKeyActions_dict[startTrack_str].append(("press", delay_fl))
                        self.m_keyTiming_dict[startTrack_str].append(self.m_curTimeStampSec_fl + delay_fl)
                    else: pass
                # increase index
                index += 1
            # after procesing, keep the remaining slice for next cycle
            lines = lines[index:]

        # clean up the timing buffer
        for timings in self.m_keyTiming_dict.values():
            while len(timings) > 0 and timings[0] + COOLDOWN < self.m_curTimeStampSec_fl: timings.pop(0) # already outdated

    def pressKey(self):
        # loop over all found actions, press the key accordingly
        for track, actions in self.m_curKeyActions_dict.items():
            for action in actions:
                if action[0] == "click": self.__newThreadClick(KEY_CONFIG[track], action[1])
                elif action[0] == "press": self.__newThreadPress(KEY_CONFIG[track], action[1])
                elif action[0] == "release": self.__newThreadRelease(KEY_CONFIG[track], action[1])
                else: pass

    def updatePrevBufferForNextCycle(self):
        self.m_prevTimeStampSec_fl = self.m_curTimeStampSec_fl
        self.m_prevDetectedLines_dict = deepcopy(self.m_curDetectedLines_dict)
        self.m_prevColorFrame = deepcopy(self.m_curColorFrame)
        self.m_prevGrayFrame = deepcopy(self.m_curGrayFrame)

    def clean(self):
        # release all the keys
        for key in KEY_CONFIG.values(): keyboard.release(key)

    def __speedAvailable_b(self):
        if self.m_elapsedPixel_int > 0 and self.m_elapsedTimeSec_fl > 0: return True
        else: return False

    def __updateWithoutSpeed(self):
        # loop over all lines and compare current with previous in order, sum up the elapsed pixel and time
        # no overflow handling necessary
        for track in self.m_prevDetectedLines_dict.keys():
            prevLines_lst = self.m_prevDetectedLines_dict[track]
            curLines_lst = self.m_curDetectedLines_dict[track]
            index = 0
            while (index < len(prevLines_lst)) and (index < len(curLines_lst)):
                self.m_elapsedPixel_int += curLines_lst[index] - prevLines_lst[index]
                self.m_elapsedTimeSec_fl += self.m_curTimeStampSec_fl - self.m_prevTimeStampSec_fl
                index += 1

    def __updateWithSpeed(self):
        # get speed
        speed_fl = float(self.m_elapsedPixel_int) / self.m_elapsedTimeSec_fl
        # get time difference
        timeDiff_fl = self.m_curTimeStampSec_fl - self.m_prevTimeStampSec_fl
        # reset and update the prediction
        for track, lines in self.m_prevDetectedLines_dict.items():
            self.m_linePredictions_dict[track] = []
            for line in lines:
                # predicted position = previous position + speed * time difference
                self.m_linePredictions_dict[track].append(int(line + speed_fl * timeDiff_fl))
        # match the prediction with new detection and update the speed
        for track in self.m_prevDetectedLines_dict.keys():
            predIndex_int = 0
            curIndex_int = 0
            predLines_lst = self.m_linePredictions_dict[track]
            prevLines_lst = self.m_prevDetectedLines_dict[track]
            curLines_lst = self.m_curDetectedLines_dict[track]
            while (predIndex_int < len(predLines_lst)) and (curIndex_int < len(curLines_lst)):
                predPosY_int = predLines_lst[predIndex_int]
                prevPosY_int = prevLines_lst[predIndex_int]
                curPosY_int = curLines_lst[curIndex_int]
                # use previous position and frame for color check
                # use predicted position for position check
                if self.__classifyLine(prevPosY_int, track, True)[0] == self.__classifyLine(curPosY_int, track)[0] and \
                   abs(predPosY_int - curPosY_int) <= LINE_MATCH_THRESHOLD:
                    self.m_elapsedPixel_int += curPosY_int - prevPosY_int # here use previous position not prediction
                    self.m_elapsedTimeSec_fl += self.m_curTimeStampSec_fl - self.m_prevTimeStampSec_fl
                    predIndex_int += 1
                    curIndex_int +=1
                elif predPosY_int > curPosY_int: predIndex_int += 1
                else: curIndex_int += 1
        # overflow handling
        if (self.m_elapsedPixel_int > MAX_ELAPSED_PIXEL) or (self.m_elapsedTimeSec_fl > MAX_ELAPSED_TIME_SEC):
            self.m_elapsedPixel_int = int(self.m_elapsedPixel_int/2)
            self.m_elapsedTimeSec_fl /= 2

    def __classifyLine(self, f_posY_int, f_track_str, prev = False):
        # based on the pixel color arround the line, decide what kind if line is detected
        # ...

        # get pixels
        posX_int = TRACK_POS_X[f_track_str]-LEFT_EDGE+int(TRACK_WIDTH/2)
        upper = self.m_curColorFrame[f_posY_int - COLOR_PICK_OFFSET][posX_int]
        lower = self.m_curColorFrame[f_posY_int + COLOR_PICK_OFFSET][posX_int]
        # classify color and layer
        upperColor, upperLayer = self.__classifyColor(upper)
        lowerColor, lowerLayer = self.__classifyColor(lower)
        # classification
        if upperLayer < lowerLayer:
            return "end", self.__decideOutputTrack_str(f_track_str, lowerColor), "none"
        elif upperLayer == lowerLayer:
            # check if we have different upper and lower color -> special handling for blue connected with red
            if not upperColor == lowerColor:
                return "both", self.__decideOutputTrack_str(f_track_str, lowerColor), self.__decideOutputTrack_str(f_track_str, upperColor)
            else: return "middle", "none", "none" # in the middle of long key
        else:
            return "start", "none", self.__decideOutputTrack_str(f_track_str, upperColor)

    def __classifyColor(self, f_pixel_npa):
        if f_pixel_npa[0] <= BGR_BLACK[0] and f_pixel_npa[1] <= BGR_BLACK[1] and f_pixel_npa[2] <= BGR_BLACK[2]:
            return "black", COLOR_LAYER["black"]
        elif f_pixel_npa[0] >= BGR_WHITE[0] and f_pixel_npa[1] >= BGR_WHITE[1] and f_pixel_npa[2] >= BGR_WHITE[2]:
            return "white", COLOR_LAYER["white"]
        elif f_pixel_npa[0] <= BGR_ORANGE[0] and f_pixel_npa[1] >= BGR_ORANGE[1] and f_pixel_npa[2] >= BGR_ORANGE[2]:
            return "orange", COLOR_LAYER["orange"]
        elif f_pixel_npa[0] >= BGR_BLUE[0] and f_pixel_npa[1] >= BGR_BLUE[1] and f_pixel_npa[2] <= BGR_BLUE[2]:
            return "blue", COLOR_LAYER["blue"]
        elif f_pixel_npa[0] >= BGR_RED[0] and f_pixel_npa[0] <= BGR_RED[1] and f_pixel_npa[1] <= BGR_RED[2] and f_pixel_npa[2] >= BGR_RED[3]:
            return "red", COLOR_LAYER["red"]
        else: return "black", COLOR_LAYER["black"] # default return black, should never reach here

    def __decideOutputTrack_str(self, f_track_str, f_color_str):
        if f_color_str == "blue":
            if "side left" in SPECIAL_KEY_MAPPING[f_track_str]: return "side left"
            else: return "side right"
        elif f_color_str == "red":
            if "left" in SPECIAL_KEY_MAPPING[f_track_str]: return "left"
            else: return "right"
        else: return f_track_str

    def __checkDuplication(self, f_track_str, f_delay_fl):
        # only for debug
        if not f_track_str in self.m_keyTiming_dict.keys(): return True

        # in case already similar trigger timing available in the buffer, return true to avoid duplicated triggering
        timings_lst = self.m_keyTiming_dict[f_track_str]
        target_fl = self.m_curTimeStampSec_fl + f_delay_fl
        index = 0

        while index < len(timings_lst):
            if target_fl < timings_lst[index] + COOLDOWN:
                timings_lst[index] = min(target_fl, timings_lst[index]) # save the earlier one
                return True
            index += 1
        return False

    def __click(self, f_key_str, f_delay_fl):
        time.sleep(f_delay_fl)
        keyboard.press_and_release(f_key_str)
    def __newThreadClick(self, f_key_str, f_delay_fl):
        t = threading.Thread(target = self.__click, args=(f_key_str, f_delay_fl))
        t.start()

    def __press(self, f_key_str, f_delay_fl):
        time.sleep(f_delay_fl)
        keyboard.press(f_key_str)
    def __newThreadPress(self, f_key_str, f_delay_fl):
        t = threading.Thread(target = self.__press, args=(f_key_str, f_delay_fl))
        t.start()

    def __release(self, f_key_str, f_delay_fl):
        time.sleep(f_delay_fl)
        keyboard.release(f_key_str)
    def __newThreadRelease(self, f_key_str, f_delay_fl):
        t = threading.Thread(target = self.__release, args=(f_key_str, f_delay_fl))
        t.start()
