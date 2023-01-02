import sys
import midiProcessing as mp
import tabProcessing as tp
import mido as m
import notes
import os
import logging
import shutil
import datetime
import re

global tuning
global maxFWidth
global capo
global tabFile
global maxFret

tuning      = "standard"
maxFWidth   = 5
capo        = 0
tabFile     = ""
maxFret     = 15

# Basic logging setup; Mainly makes use of the logging module
def loggerSetup():
    try:
        os.mkdir(os.path.join(".", "log"))
    except FileExistsError:
        pass
    if (os.path.exists(os.path.join(".", "log", "error.log"))):
        try:
            os.mkdir(os.path.join(".", "log", "archive"))
        except FileExistsError:
            pass
        modDate = os.path.getmtime(os.path.join(".", "log", "error.log"))
        dtModDate = datetime.datetime.fromtimestamp(modDate).strftime("%Y-%m-%d_%H%M%S")
        shutil.move (os.path.join(".", "log", "error.log"), os.path.join(".","log","archive",f"error_{str(dtModDate)}.log"))
    logging.basicConfig(
    filename = os.path.join(".", "log", "error.log"),
    level = logging.DEBUG,
    style = '{',
    format = "{asctime}    [ {levelname:7} ]       {message}"
    )
    return logging.getLogger()

# Processes all arguments; Currently only has options available for:
# -i: Input file name
# -t: Tuning name
# -f: Maximum playable fret
# -w: Maximum finger width
# -c: Capo position
def processArgs(argv):
    argvLowFlag = []
    for arg in sys.argv[1:]:
        argvLowFlag.append(arg[0:2].lower() + arg[2:])
    if (any("-i" in arg for arg in argvLowFlag)):
        for arg in argvLowFlag:
            match arg[0:2]:
                case "-i":
                    global iFileName
                    iFileName = arg[2:]
                    if not re.match(".*\.mid", iFileName):
                        print (f"Error - Specified input file was not a MIDI file: {iFileName}")
                        logging.error (f"Error - Specified input file was not a MIDI file: {iFileName}")
                        exit()
                case "-t":
                    global tuning
                    tuning = arg[2:]
                case "-f":
                    global maxFret
                    maxFret = int(arg[2:])
                case "-w":
                    global maxFWidth
                    maxFWidth = int(arg[2:])
                case "-c":
                    global capo
                    capo = int(arg[2:])

# The main function; Basically calls all other necessary functions from beginning to end
# 1. Quantizes the MIDI file to eighth notes
# 2. Generates a bare bones MIDI file from 1
# 3. Generates a table of playable notes according to the selected tuning, capo, playable fret, etc.
# 4. Generates tabulature from the bare bones MIDI and the ntoe table from 3
# 5. Pretty prints onto a new text file
def main(iFileName, tuning = "standard", maxFWidth = 5, capo = 0, maxFret = 15):
    # Default output format
    global tabFile
    if tabFile == "":
        tabFile = os.path.join(".", "output",f"{iFileName[:-4]}", "tab.txt")
        logging.info (f"Output file located: {tabFile}")
    try:
        os.mkdir(os.path.join(".", "output"))
    except FileExistsError:
        logging.debug (f"output folders already exist")
        pass
    try:
        os.mkdir(os.path.join(".", "output", f"{iFileName[:-4]}"))
        logging.debug (f"Created the following folder:{os.mkdir(os.path.join('.', 'output'))}")
    except FileExistsError:
        logging.debug (f"output folders already exist")
        pass

    noteTime, tpb, tempo = mp.quantizeMIDI(iFileName)                                                           #1
    mp.generateMIDI(noteTime, tpb, tempo, oFileName = os.path.join("output", iFileName[:-4], "quantized.mid"))  #2
    noteTable = notes.generateNoteTable(iTuning = tuning, capo = capo, maxFret = maxFret)                       #3
    tabs = mp.notesToTabs (noteTime, tpb, tempo, noteTable, maxFWidth)                                          #4
    tp.tabPrettyPrint (tabs, tabFile)                                                                           #5
    print (f"Tabs successfully generated: {tabFile}")
    logging.info (f"Tabs successfully generated: {tabFile}")

# Basic setup; Sets up logging and checks if there are any input variables; If not, explain to the user how to use the program
if __name__ == "__main__":
    logger = loggerSetup()
    if (sys.argv[1:]):
        processArgs(sys.argv[1:])
        main(iFileName, tuning, maxFWidth, capo, maxFret)
    else:
        print ("This script generates guitar tabulature from a MIDI file. ")
        print ("The input arguments are as follows:")
        print ("        -i<input file name>               The input MIDI file you want to generate tabulature from"     )
        print ("        -t<Tuning>                        Tuning that will be used. Can be configured in notes.py;"     )
        print ("                                          The following are available by default: standard, dropd,"     )
        print ("                                          dadgad, facgce; Default value of standard"                    )
        print ("        -f<max playable fret>             The maximum playable fret; Default value of 15"               )
        print ("        -w<max finger width>              How many frets your finger can span; Default value of 5"      )
        print ("        -c<capo>                          Capo position; Default value of 0"                            )
        logging.info ("Exited without an input file")