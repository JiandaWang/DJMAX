import cv2
import numpy as np

USE_CUDA = True
BINARY_THRESH = 150
CANNY_LOW_THRESH = 50
CANNY_HIGH_THRESH = 150
GRADIENT_THRESH = 100 # technically any value should be fine since used for black/white frame

class CTrack():
    def __init__(self,
                 f_key_str="",
                 f_posX_int=0,
                 f_notes_lst=[]
                ):
        self.m_key_str = f_key_str
        self.m_posX_int = f_posX_int
        self.m_notes_lst = f_notes_lst

class CNote():
    def __init__(self,
                 f_startPos_b = True,
                 f_PosY_int = -1):
        self.m_startPos_b = f_startPos_b
        self.m_PosY_int = f_PosY_int

def DetectNotesInTracks(f_config, f_frame):
    # initialize output
    tracks = []

    # separate tracks based on config file
    for key, posX in f_config.m_keyToTrackPosXs_dict.items():
        # detect lines -> only posY output since only horizontal line
        grayFrame, linePosYList_lst = DetectLines(f_config,
                                                  posX,
                                                  f_frame)

        # based on detected lines, detect notes
        track = DetectNotesInTrack(f_config,
                                   grayFrame,
                                   key,
                                   linePosYList_lst)
        
        # append to output
        tracks.append(track)
    
    return tracks

def DetectLines(f_config, f_startPosX_int, f_frame):
    # initialize output
    linePosYList_lst = []

    # get cropped frame
    croppedFrame = f_frame[0:f_config.m_noteDetectionLinePosY_int,
                           f_startPosX_int:f_startPosX_int+f_config.m_trackWidth_int]
    # get grayscale frame
    # this conversion need to be at begining, to be able to handle np array like
    # screenshots from mss directly
    grayFrame = cv2.cvtColor(croppedFrame, cv2.COLOR_BGR2GRAY)
    # apply bilateral filter to smooth the input while keeping the edge detail
    grayFrame = cv2.bilateralFilter(grayFrame, 7, 60, 60)
    # do binary filtering to get rid of combo text
    _, grayFrame = cv2.threshold(grayFrame, BINARY_THRESH, 255, cv2.THRESH_BINARY)

    # apply canny edge detection
    edges = cv2.Canny(grayFrame, CANNY_LOW_THRESH, CANNY_HIGH_THRESH)

    # apply hough transformation to find line
    # thresholds depend on track width so that they can automatically adjusted
    lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                            threshold=int(f_config.m_trackWidth_int/4),
                            minLineLength=int(f_config.m_trackWidth_int/2),
                            maxLineGap=int(f_config.m_trackWidth_int/8))

    # iterate over contours and find horizontal lines
    if not lines is None:
        for line in lines:
            # get the coordinates
            _, y1, _, y2 = line[0]
            # check if horizontal -> if yes, output the average posY
            if abs(y2 - y1) <= (f_config.m_noteHeight_int/4): linePosYList_lst.append(int((y1+y2)/2))
    
    return grayFrame, linePosYList_lst

def DetectNotesInTrack(f_config, f_frame, 
                       f_key_str,
                       f_linePosYList_lst):
    # initialize track object
    track = CTrack(f_key_str=f_key_str,
                   f_posX_int=f_config.m_keyToTrackPosXs_dict[f_key_str],
                   f_notes_lst=[])

    # sort the posY list descending 
    # -> to be able to handle from the lowest note
    linePosYSorted_lst = f_linePosYList_lst.copy()
    linePosYSorted_lst.sort(reverse=True)

    # loop over all posY in the list
    for posY in linePosYSorted_lst:
        # check whether start / end pos can be classified
        classResult_int = classifyPosY(f_config, f_frame, posY)
        if classResult_int > 0:
            # save with startPos_b = True
            track.m_notes_lst.append(CNote(True, posY))
        elif classResult_int < 0:
            # save with startPos_b = False
            track.m_notes_lst.append(CNote(False, posY))
        else: pass # do nothing
    
    return track

def classifyPosY(f_config, f_frame, f_posY_int):
    # get the frame size
    height_int, _, = f_frame.shape # only two values here due to grayscale frame...

    # set lower and higher pixel posY to be examed
    lowerPosY_int = f_posY_int + int(f_config.m_noteHeight_int/2)
    higherPosY_int = f_posY_int - int(f_config.m_noteHeight_int/2)

    # in case any pos exceeds the range, return 0
    if lowerPosY_int > height_int-1 or higherPosY_int < 0: return 0

    # otherwise get the value of those pixels can calculate the difference
    # take the pixel from the middle of the frame
    posX_int = int(f_config.m_trackWidth_int/2)
    lowerPixelVal_int = int(f_frame[lowerPosY_int, posX_int])
    higherPixelVal_int = int(f_frame[higherPosY_int, posX_int])
    pixelValDiff_int = lowerPixelVal_int - higherPixelVal_int
    if pixelValDiff_int < GRADIENT_THRESH: return 1 # start pos; lower black + higher white
    elif pixelValDiff_int > GRADIENT_THRESH: return -1 # end pos; lower white + higher black
    else: return 0