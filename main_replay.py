from configs import *
from master import *
import pickle
import cv2
from copy import deepcopy

def visualization(f_debugSlice, f_mode_str):
    # set parameter based on mode
    if f_mode_str == 'debug':
        waitTime_int = 0
        fullDetectWindowPosX_int = int(DEBUG_MONITOR_WIDTH / 2)
        fullDetectWindowPosY_int = int((DEBUG_MONITOR_HEIGHT - JUDGE_LINE_POS_Y) / 2)
        cannyEdgesWindowPosX_int = int(DEBUG_MONITOR_WIDTH / 2) - (RIGHT_EDGE - LEFT_EDGE)
        cannyEdgesWindowPosY_int = fullDetectWindowPosY_int
    else:
        waitTime_int = 1
        fullDetectWindowPosX_int = RIGHT_EDGE + int(GAME_MONITOR_WIDTH / 16) - GAME_MONITOR_WIDTH
        fullDetectWindowPosY_int = 0
        cannyEdgesWindowPosX_int = LEFT_EDGE - (RIGHT_EDGE - LEFT_EDGE) - int(GAME_MONITOR_WIDTH / 16) - GAME_MONITOR_WIDTH
        cannyEdgesWindowPosY_int = fullDetectWindowPosY_int

    ############################################ canny window #############################################
    cv2.imshow('CannyEdges', f_debugSlice.m_cannyFrame)
    cv2.setWindowProperty("CannyEdges", cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow("CannyEdges", cannyEdgesWindowPosX_int, cannyEdgesWindowPosY_int)

    ######################################## full detection window ########################################
    # get frame
    frame = f_debugSlice.m_curColorFrame

    # plot time
    formatTime_str = "{:.4f}".format(f_debugSlice.m_curTimeStampSec_fl)
    cv2.putText(frame, formatTime_str, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

    # plot key action
    textPos_int = 20
    for track, actions in f_debugSlice.m_curKeyActions_dict.items():
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
    
    detectedLines = f_debugSlice.m_curDetectedLines_dict
    for key, lines in detectedLines.items():
        for posY in lines:
            cv2.line(frame, 
                     (TRACK_POS_X[key]-LEFT_EDGE+int(TRACK_WIDTH/2), posY),
                     (TRACK_POS_X[key]-LEFT_EDGE+TRACK_WIDTH, posY),
                     (0, 255 ,0),
                     2
                    )
    linePredictions = f_debugSlice.m_linePredictions_dict
    for key, lines in linePredictions.items():
        for posY in lines:
            cv2.line(frame, 
                     (TRACK_POS_X[key]-LEFT_EDGE, posY),
                     (TRACK_POS_X[key]-LEFT_EDGE+int(TRACK_WIDTH/2), posY),
                     (0, 0 ,255), #BGR
                     2
                    )

    cv2.imshow('FullDetect', frame)
    cv2.setWindowProperty("FullDetect", cv2.WND_PROP_TOPMOST, 1)
    cv2.moveWindow("FullDetect", fullDetectWindowPosX_int, fullDetectWindowPosY_int)

    # hold all windows
    cv2.waitKey(waitTime_int)

if __name__ == "__main__":
    # read pickle file
    with open("debugBuffer.pkl", 'rb') as f:
        debugBuffer = pickle.load(f)

    # loop over debug cycles
    for index in range(0,len(debugBuffer)):
        # replay detect key action
        temp_master = deepcopy(debugBuffer[index])
        temp_master.decideKeyAction()

        # visualization
        visualization(debugBuffer[index], "debug")
