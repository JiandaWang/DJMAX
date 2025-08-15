from configs import *
from master import *
import pickle
import cv2
from copy import deepcopy

# read pickle file
with open("debugBuffer.pkl", 'rb') as f:
    debugBuffer = pickle.load(f)

# loop over debug cycles
for index in range(0,len(debugBuffer)):
    # get frame
    frame = debugBuffer[index].m_curColorFrame

    # replay detect key action
    temp_master = deepcopy(debugBuffer[index])
    temp_master.decideKeyAction()

    # plot time
    formatTime_str = "{:.4f}".format(debugBuffer[index].m_curTimeStampSec_fl)
    cv2.putText(frame, formatTime_str, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

    # plot key action
    textPos_int = 20
    for track, actions in debugBuffer[index].m_curKeyActions_dict.items():
        for action in actions:
            formatDelay_str = "{:.4f}".format(action[1])
            text_str = track + " " + action[0] + " " + formatDelay_str
            textPos_int += 20
            cv2.putText(frame, text_str, (20, textPos_int), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

    # draw lines
    cv2.line(frame, 
             (0, NOTE_DETECT_END_LINE_POS_Y),
             (RIGHT_EDGE-LEFT_EDGE, NOTE_DETECT_END_LINE_POS_Y),
             (0, 255 ,255),
             1
            )
    cv2.line(frame, 
             (0, KEY_ACTION_LINE_POS_Y),
             (RIGHT_EDGE-LEFT_EDGE, KEY_ACTION_LINE_POS_Y),
             (0, 255 ,255),
             1
            )
    
    detectedLines = debugBuffer[index].m_curDetectedLines_dict
    for key, lines in detectedLines.items():
        for posY in lines:
            cv2.line(frame, 
                     (TRACK_POS_X[key]-LEFT_EDGE+int(TRACK_WIDTH/2), posY),
                     (TRACK_POS_X[key]-LEFT_EDGE+TRACK_WIDTH, posY),
                     (0, 255 ,0),
                     2
                    )
    linePredictions = debugBuffer[index].m_linePredictions_dict
    for key, lines in linePredictions.items():
        for posY in lines:
            cv2.line(frame, 
                     (TRACK_POS_X[key]-LEFT_EDGE, posY),
                     (TRACK_POS_X[key]-LEFT_EDGE+int(TRACK_WIDTH/2), posY),
                     (0, 0 ,255), #BGR
                     2
                    )

    cv2.imshow('Frame', frame)
    cv2.waitKey()
