import collections as col

# Tunings are stored in an array of length 6 (one for each string); In this case, index 0 is the lowest string/one closest to the user
# Tunings can be added by matching MIDI notes to the open string
Tunings = {
        "standard" : [40, 45, 50, 55, 59, 64],
        "dropd"    : [38, 45, 50, 55, 59, 64],
        "dadgad"   : [38, 45, 50, 55, 57, 62],
        "facgce"   : [53, 57, 60, 67, 72, 76]
}

# The following function goes through each playable note according to the chosen tuning and encodes them.
# Playable notes are stored in a 3 digit value: The concatenation of the string being picked and the fret to play that string.
# Example a G Chord would be as follows:
# 103 -> 1 03: 3rd fret on 1st string               -----3-----
# 202 -> 2 02: 2nd fret on 2nd string               -----2-----
# 300 -> 3 00: Open 3rd string                      -----0-----
# 300 -> 4 00: Open 4th string                      -----0-----
# 300 -> 5 00: Open 5th string                      -----0-----
# 603 -> 6 03: 3rd fret on the sixth string         -----3-----
def generateNoteTable(iTuning = "standard", maxFret = 15, capo = 0):
    if iTuning in Tunings:
        tuning = Tunings[iTuning]
    else:
        tuning = Tunings["standard"]
    # Creates an entry for all notes playable in the current string range
    # Can be further refined in case that some strings have no overlap
    noteTable = {i : [] for i in range (tuning[0] + capo, tuning[-1] + maxFret + 1 + capo)}
    for index, string in enumerate(tuning):
        for fret in range (capo, maxFret + 1):
            noteTable[string + fret].append(100 + index*100 + fret - capo)
    # Sorts the table to prefer open strings when generating tabulature
    for note, fretting in noteTable.items():
        fretting.sort(key = lambda x:x%100)
    return noteTable

# Not currently being used; Will be used when mp3 inputs are accepted for audio processing
frequencytoMIDI = col.OrderedDict([
#     |       B       |      A#      |     A     |       G#     |       G       |       F#      |        F      |        E      |        D#     |       D       |      C#       |       C       |
                                                                  (12543.85,127), (11839.82,126), (11175.3,125) , (10548.08,124), (9956.06,123) , (9397.27,122) , (8869.84,121) , (8372.02,120) ,
        (7902.13,119) , (7458.62,118), (7040,117), (6644.88,116), (6271.93,115) , (5919.91,114) , (5587.65,113) , (5274.04,112) , (4978.03,111) , (4698.64,110) , (4434.92,109) , (4186.01,108) ,
        (3951.07,107) , (3729.31,106), (3520,105), (3322.44,104), (3135.96,103) , (2959.96,102) , (2793.83,101) , (2637.02,100) , (2489.02,99)  , (2349.32,98)  , (2217.46,97)  , (2093,96)     ,
        (1975.53,95)  , (1864.66,94) , (1760,93) , (1661.22,92) , (1567.98,91)  , (1479.98,90)  , (1396.91,89)  , (1318.51,88)  , (1244.51,87)  , (1174.66,86)  , (1108.73,85)  , (1046.5,84)   ,
        (987.77,83)   , (932.33,82)  , (880,81)  , (830.61,80)  , (783.99,79)   , (739.99,78)   , (698.46,77)   , (659.26,76)   , (622.25,75)   , (587.33,74)   , (554.37,73)   , (523.25,72)   ,
        (493.88,71)   , (466.16,70)  , (440,69)  , (415.3,68)   , (392,67)      , (369.99,66)   , (349.23,65)   , (329.63,64)   , (311.13,63)   , (293.66,62)   , (277.18,61)   , (261.63,60)   ,
        (246.94,59)   , (233.08,58)  , (220,57)  , (207.65,56)  , (196,55)      , (185,54)      , (174.61,53)   , (164.81,52)   , (155.56,51)   , (146.83,50)   , (138.59,49)   , (130.81,48)   ,
        (123.47,47)   , (116.54,46)  , (110,45)  , (103.83,44)  , (98,43)       , (92.5,42)     , (87.31,41)    , (82.41,40)    , (77.78,39)    , (73.42,38)    , (69.3,37)     , (65.41,36)    ,
        (61.74,35)    , (58.27,34)   , (55,33)   , (51.91,32)   , (49,31)       , (46.25,30)    , (43.65,29)    , (41.2,28)     , (38.89,27)    , (36.71,26)    , (34.65,25)    , (32.7,24)     ,
        (30.87,23)    , (29.14,22)   , (27.5,21) , (25.96,20)   , (24.5,19)     , (23.12,18)    , (21.83,17)    , (20.6,16)     , (19.45,15)    , (18.35,14)    , (17.32,13)    , (16.35,12)    ,
        (15.43,11)    , (14.57,10)   , (13.75,9) , (12.98,8)    , (12.25,7)     , (11.56,6)     , (10.91,5)     , (10.3,4)      , (9.72,3)      , (9.18,2)      , (8.66,1)      , (8.18,0)
])