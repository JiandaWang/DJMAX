from detect_notes import *
from copy import deepcopy
import keyboard
import time

MAX_ELAPSED_PIXEL = 100000
MAX_ELAPSED_TIME_SEC = 40

# this parameter would be used later for trigger tolerance calculation
# based on current estimated speed
# it can be set to negative too, which means the triggering of the key
# would be delayed after note crossing the judge line
# note if this value is too much negative all the notes would be ignored
# since such kind of a delay would be not meaningful
TRIGGER_TOL_SEC = 0.11

# this parameter defines how long the click will hold the key
# this value should be considerable longer than (1/game check rate), otherwise
# the click itself will not be recognized by the game
# this value should also not be longer than the cycle time, otherwise there
# could be notes got overriden by this click
CLICK_HOLD_SEC = 0.015

class CMaster():
    def __init__(self,
                 f_config,
                 f_debug_b=False
                ):
        # time stamp of last update
        self.m_timeStampSec_fl = 0

        # save elapsed pixels and time for note falling speed estimation
        self.m_elapsedPixel_int = int(0)
        self.m_elapsedTimeSec_fl = 0

        # based on configuration file, prepare the tracks
        self.m_idx_dict = {}
        self.m_tracks_lst = []
        self.m_keyStatus_dict = {}
        idx = int(0)
        for key, posX in f_config.m_keyToTrackPosXs_dict.items():
            self.m_idx_dict[key] = idx
            self.m_tracks_lst.append(CTrack(f_key_str=key,
                                            f_posX_int=posX,
                                            f_notes_lst=[]))
            self.m_keyStatus_dict[key] = "None"
            keyboard.release(key) # also release the keys
            idx += 1
        
        # based on cofiguration file, save the different tolerances
        self.m_matchTolerance_int = int(f_config.m_noteHeight_int/2)
        self.m_triggerPosY_int = f_config.m_judgeLinePosY_int
        self.m_noteHeightWithTol_int = int(f_config.m_noteHeight_int*1.2)
        self.m_triggerTolerance_int = 0 # calculate based on speed each cycle

        # debug related attributes
        self.m_debug_b = f_debug_b
        self.m_keyLogPerCycle_lst = []

    def update(self, f_currentTimeSec_fl, f_tracks_lst):
        # in case debug in on, reset the key log
        if self.m_debug_b: self.m_keyLogPerCycle_lst = []

        # get current speed
        speedAvailable_b, speed_fl = self.__getSpeed()
        self.m_triggerTolerance_int = int(speed_fl*TRIGGER_TOL_SEC)

        # check if speed available
        if speedAvailable_b:
            self.__updateMasterWithSpeed(f_currentTimeSec_fl, f_tracks_lst, speed_fl)

        else: 
            # speed not available -> should only be reached at very begin
            # OPEN POINT: sound track with various speed range?
            self.__updateMasterWithOutSpeed(f_currentTimeSec_fl, f_tracks_lst)

    def updateKey(self, f_config, f_colorFrame):
        # loop over tracks
        for track in self.m_tracks_lst:
            # techinically only check the first note should be enough
            # based on the note pos and type, decide wether click, press or release the key

            # get the color on note detection line
            # colorPosY_int = f_config.m_noteDetectionLinePosY_int
            # colorPosX_int = track.m_posX_int+int(f_config.m_trackWidth_int/2)
            # pixel_npa = f_colorFrame[colorPosY_int, colorPosX_int]
            # grayScale_int = cv2.cvtColor(np.array([[pixel_npa]]), cv2.COLOR_BGR2GRAY)[0][0]

            # reset click status from last update
            # in few cases, a click case could be wrongly detected as press
            # if on the track there is no color, the key should be released
            # due to accuracy percentage display, the color would be taken from
            # frame clipping position of the note detection
            if    self.m_keyStatus_dict[track.m_key_str] == "Click":
                self.m_keyStatus_dict[track.m_key_str] = "None"
            # elif    self.m_keyStatus_dict[track.m_key_str] == "Press" \
            #     and grayScale_int < BINARY_THRESH:
            #     self.m_keyStatus_dict[track.m_key_str] = "None"
            #     keyboard.release(track.m_key_str)

            # in case currently the key status is none, but the first note is end pos
            # -> not sense making, skip it
            if self.m_keyStatus_dict[track.m_key_str] == "None":
                while (    (len(track.m_notes_lst)>0) \
                       and (not track.m_notes_lst[0].m_startPos_b)):
                    track.m_notes_lst.pop(0)

            # if no information -> skip the track
            if len(track.m_notes_lst) == 0: continue

            # in case debug in on, get the current time
            if self.m_debug_b: curTime_fl = time.time()

            # only proceed when the distance is close enough
            if track.m_notes_lst[0].m_PosY_int + self.m_triggerTolerance_int >= self.m_triggerPosY_int:
                # in case it's end pos, release the key and pop out the first element
                if not track.m_notes_lst[0].m_startPos_b:
                    self.m_keyStatus_dict[track.m_key_str] = "None"
                    keyboard.release(track.m_key_str)
                    track.m_notes_lst.pop(0)
                    # debug key log
                    if self.m_debug_b: self.m_keyLogPerCycle_lst.append([track.m_key_str, "Release", curTime_fl])
                else: # the note is a start pos
                    if len(track.m_notes_lst) == 1:
                        # no other information available
                        # do a press and pop the note
                        self.m_keyStatus_dict[track.m_key_str] = "Press"
                        keyboard.press(track.m_key_str)
                        track.m_notes_lst.pop(0)
                        # debug key log
                        if self.m_debug_b: self.m_keyLogPerCycle_lst.append([track.m_key_str, "Press", curTime_fl])
                    else: # there are other notes available
                        # due to unstable screenshot performance, there could be note
                        # information which are very close to each other, but represent
                        # the same note
                        # we consider all notes within the note height tolerance,
                        # which can be considered as same note
                        firstStartPosY_int = track.m_notes_lst[0].m_PosY_int
                        track.m_notes_lst.pop(0)
                        endPosFound_b = False
                        while (   (len(track.m_notes_lst)>0) 
                               and(firstStartPosY_int - track.m_notes_lst[0].m_PosY_int <= self.m_noteHeightWithTol_int)):
                            if not track.m_notes_lst[0].m_startPos_b: endPosFound_b = True
                            track.m_notes_lst.pop(0)
                        
                        # if end pos found, do a click
                        if endPosFound_b: 
                            self.m_keyStatus_dict[track.m_key_str] = "Click"
                            keyboard.press(track.m_key_str)
                            keyboard.call_later(keyboard.release, track.m_key_str, CLICK_HOLD_SEC)
                            # debug key log
                            if self.m_debug_b: 
                                self.m_keyLogPerCycle_lst.append([track.m_key_str, "Click", curTime_fl])
                                self.m_keyLogPerCycle_lst.append([track.m_key_str, "Click_Release", curTime_fl+CLICK_HOLD_SEC])
                        else: # otherwise do a press
                            self.m_keyStatus_dict[track.m_key_str] = "Press"
                            keyboard.press(track.m_key_str)
                            # debug key log
                            if self.m_debug_b: self.m_keyLogPerCycle_lst.append([track.m_key_str, "Press", curTime_fl])

    def __getSpeed(self):
        if self.m_elapsedPixel_int > 0 and self.m_elapsedTimeSec_fl > 0:
            return True, float(self.m_elapsedPixel_int)/float(self.m_elapsedTimeSec_fl)
        else: 
            return False, 0

    def __updateMasterWithSpeed(self, f_currentTimeSec_fl, f_tracks_lst, f_speed_fl):
        # get time diff
        timeDiffSec_fl = f_currentTimeSec_fl - self.m_timeStampSec_fl

        # loop over all tracks
        for track in f_tracks_lst:
            # get key and corresponding idx
            key_str = track.m_key_str
            idx_int = self.m_idx_dict[key_str]

            # do pos estimation for master track information
            noteEstimation_lst = self.__posEstimation(timeDiffSec_fl, self.m_tracks_lst[idx_int].m_notes_lst, f_speed_fl)

            # match the estimation with new track information and set it back to master
            self.m_tracks_lst[idx_int].m_notes_lst = self.__matchNotes(timeDiffSec_fl,
                                                                       self.m_tracks_lst[idx_int].m_notes_lst, 
                                                                       noteEstimation_lst, 
                                                                       track.m_notes_lst)

        # update time stamp
        self.m_timeStampSec_fl = f_currentTimeSec_fl 

    def __posEstimation(self, f_timeDiffSec_fl, f_notes_lst, f_speed_fl):
        # initialize output
        notesOut_lst = deepcopy(f_notes_lst)

        # calculate pixel shift
        pixelShift_int = int(f_speed_fl * f_timeDiffSec_fl)

        # loop over all notes
        for note in notesOut_lst: note.m_PosY_int += pixelShift_int

        return notesOut_lst

    def __matchNotes(self, f_timeDiffSec_fl, f_masterNotes_lst, f_noteEstimation_lst, f_newNotes_lst):
        # initialize empty output
        matchedNotes_lst = []

        # check note from both notes list one by one
        # if the pos matches with certain tolerance and type also matched,
        # append new note into output since its position should be precise
        # otherwise append the one with lower pos into output and
        # check next possible combination
        # * if pos are the same but different type, append start pos
        lenEst_int = len(f_noteEstimation_lst)
        lenNew_int = len(f_newNotes_lst)
        idxEst_int = int(0)
        idxNew_int = int(0)
        while ((idxEst_int < lenEst_int) and (idxNew_int < lenNew_int)):
            # get notes
            estNote = f_noteEstimation_lst[idxEst_int]
            newNote = f_newNotes_lst[idxNew_int]
            # check match condition
            if    estNote.m_startPos_b == newNote.m_startPos_b \
              and abs(estNote.m_PosY_int - newNote.m_PosY_int) <= self.m_matchTolerance_int:
                # append new note
                matchedNotes_lst.append(newNote)
                # since master and estimation note lists are one by one paired,
                # same index can be used -> update master notes for speed update
                self.__updateSpeedEstimation(f_masterNotes_lst[idxEst_int],
                                             newNote,
                                             f_timeDiffSec_fl
                                            )
                # increase both index
                idxEst_int += 1
                idxNew_int += 1
            else:
                if estNote.m_PosY_int > newNote.m_PosY_int:
                    matchedNotes_lst.append(estNote)
                    idxEst_int += 1
                elif estNote.m_PosY_int < newNote.m_PosY_int:
                    matchedNotes_lst.append(newNote)
                    idxNew_int += 1
                else:
                    if estNote.m_startPos_b:
                        matchedNotes_lst.append(estNote)
                        idxEst_int += 1
                    else:
                        matchedNotes_lst.append(newNote)
                        idxNew_int += 1

        # append remaining notes into output
        # the order should be fine since only note from one list can be left, if any
        while (idxEst_int < lenEst_int):
            estNote = f_noteEstimation_lst[idxEst_int]
            matchedNotes_lst.append(estNote)
            idxEst_int += 1
        while (idxNew_int < lenNew_int):
            newNote = f_newNotes_lst[idxNew_int]
            matchedNotes_lst.append(newNote)
            idxNew_int += 1

        return matchedNotes_lst

    def __updateMasterWithOutSpeed(self, f_currentTimeSec_fl, f_tracks_lst):
        # get time diff
        timeDiffSec_fl = f_currentTimeSec_fl - self.m_timeStampSec_fl

        # loop over all tracks
        for track in f_tracks_lst:
            # get key and corresponding idx
            key_str = track.m_key_str
            idx_int = self.m_idx_dict[key_str]

            # in case both master track and new track has information
            # update speed estimation related counter
            lenMaster_int = len(self.m_tracks_lst[idx_int].m_notes_lst)
            lenNew_int = len(track.m_notes_lst)
            if lenMaster_int > 0 and lenNew_int > 0:
                # due to no speed information available, no matching possible
                # therefor old and new information will be compared by order simply
                # note: this speed estimation is based on the assumption that at least
                #       at very beginning the first two notes from two screen captures
                #       can be detected stable and correctly
                #       if it would be not the case, the estimated speed has a high 
                #       possibility to be wrong
                #       therefor if the first two notes not "match" each other, the speed
                #       estimation would be shifted to next cycle
                idxMaster_int = int(0)
                idxNew_int = int(0)
                while ((idxMaster_int < lenMaster_int) and (idxNew_int < lenNew_int)):
                    # get notes
                    masterNote = self.m_tracks_lst[idx_int].m_notes_lst[idxMaster_int]
                    newNote = track.m_notes_lst[idxNew_int]
                    # speed estimation only make sense when both notes are same type and
                    # new note should have a lower position
                    if    masterNote.m_startPos_b == newNote.m_startPos_b \
                      and masterNote.m_PosY_int < newNote.m_PosY_int: 
                        # update speed estimation
                        self.__updateSpeedEstimation(masterNote,
                                                     newNote,
                                                     timeDiffSec_fl)
                        # increase index
                        idxMaster_int += 1
                        idxNew_int += 1
                    else: break # no further handling, break the loop

            # due to no speed information available, overwrite old information
            # -> even if there is no new information available
            # -> otherwise the information will not match new time stamp
            self.m_tracks_lst[idx_int].m_notes_lst = deepcopy(track.m_notes_lst)
        
        # update time stamp
        self.m_timeStampSec_fl = f_currentTimeSec_fl
    
    def __updateSpeedEstimation(self, f_oldNote, f_newNote, f_timeDiffSec_fl):
        # always assume input valid!!!
        self.m_elapsedPixel_int += f_newNote.m_PosY_int - f_oldNote.m_PosY_int
        self.m_elapsedTimeSec_fl += f_timeDiffSec_fl

        # overflow handling
        if   self.m_elapsedPixel_int > MAX_ELAPSED_PIXEL \
          or self.m_elapsedTimeSec_fl > MAX_ELAPSED_TIME_SEC:
            self.m_elapsedPixel_int = int(self.m_elapsedPixel_int/2)
            self.m_elapsedTimeSec_fl = int(self.m_elapsedTimeSec_fl/2)
