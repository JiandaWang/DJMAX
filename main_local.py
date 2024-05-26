import cv2
from configs import *
from master_control import *
from detect_notes import *
import pickle

# load data from saved pickle file
with open("config.pkl", 'rb') as f:
    config = pickle.load(f)

with open("masterCache.pkl", 'rb') as f:
    masterCacheList_lst = pickle.load(f)

with open("mssCache.pkl", 'rb') as f:
    mssCacheList_lst = pickle.load(f)

with open("trackCache.pkl", 'rb') as f:
    trackCacheList_lst = pickle.load(f)

# process the frames
for index in range(0,len(mssCacheList_lst)):
    # get slice by index
    master = masterCacheList_lst[index]
    frame = mssCacheList_lst[index]
    tracks_lst = trackCacheList_lst[index]

    # draw notes detected from master side (with estimation)
    for track in master.m_tracks_lst:
        for note in track.m_notes_lst:
            if note.m_startPos_b: noteColor = (0, 255, 0)
            else: noteColor = (0, 0, 255)

            cv2.line(frame, 
                     (track.m_posX_int, note.m_PosY_int),
                     (track.m_posX_int+int(config.m_trackWidth_int/2), note.m_PosY_int),
                     noteColor,
                     2
                    )

    # draw notes detected from current cycle
    for track in tracks_lst:
        for note in track.m_notes_lst:
            if note.m_startPos_b: noteColor = (255, 125, 0)
            else: noteColor = (0, 255, 255)

            cv2.line(frame, 
                     (track.m_posX_int+int(config.m_trackWidth_int/2), note.m_PosY_int),
                     (track.m_posX_int+config.m_trackWidth_int, note.m_PosY_int),
                     noteColor,
                     2
                    )

    # draw if at some track the key should be pressed
    for key, keyStatus in master.m_keyStatus_dict.items():
        posX_int = master.m_tracks_lst[master.m_idx_dict[key]].m_posX_int

        if keyStatus == "Click":
            cv2.rectangle(frame,
                          (posX_int, config.m_judgeLinePosY_int - config.m_noteHeight_int),
                          (posX_int + config.m_trackWidth_int, config.m_judgeLinePosY_int),
                          (0, 255, 0),
                          5
                         )

        if keyStatus == "Press":
            cv2.rectangle(frame,
                          (posX_int, config.m_judgeLinePosY_int - config.m_noteHeight_int),
                          (posX_int + config.m_trackWidth_int, config.m_judgeLinePosY_int),
                          (0, 0, 255),
                          5
                         )

    cv2.imshow('Frame', frame)
    cv2.waitKey()
