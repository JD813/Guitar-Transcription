import mido as m
import math
import collections as col
import notes
import itertools
import logging
import tabProcessing as tp

logger = logging.getLogger(__name__)

# This function generates a MIDI file from an input noteTime dictionary. This dictionary has the number of absolute ticks as the key and the notes to play at that tick as the value
# This has so far been untested for multi-track MIDIs
def generateMIDI(noteTime, tpb, tempo, oFileName):
    logger.info ("Generating cleaned MIDI file for future reference")

    # It is assumed that the tempo is the same throughout the entire song
    oFile = m.MidiFile(ticks_per_beat=tpb)
    oTrack = m.MidiTrack()
    oFile.tracks.append(oTrack)
    oTrack.append(m.Message('program_change', channel=0, program=0, time=0))
    oTrack.append(m.MetaMessage('set_tempo', tempo=tempo, time=0))

    # As we are generating simple tabulature, note duration/velocity are not taken into account
    prevKey = 0
    absTicks = 0

    # Generates a basic MIDI file for future reference/editing
    for key, value in noteTime.items():
        logger.debug ("------------------------------------------------------------------------------")
        tickDiff = int(key - prevKey)
        absTicks += tickDiff

        # Generate a "note on" message for each note to play at the current tick value
        logger.debug (f"| Current Tick (abs) | Previous Tick (abs) | Tick Difference | Notes to Play |")
        logger.debug (f"| {absTicks:18} | {prevKey:19} | {tickDiff:15} | {str(value):13} |")
        for i, mNote in enumerate(value):
            oTrack.append(m.Message("note_on", note=mNote, velocity=127, time=tickDiff))
            pString = f"| note_on channel=0 note={mNote} velocity=127 time={tickDiff})"
            logger.debug (f"{pString:76} |")
            tickDiff = 0

        # Generate a "note off" message an eighth of a measure after the note on
        tickDiff = int(_8th)
        absTicks += tickDiff
        for mNote in value:
            oTrack.append(m.Message("note_off", note=mNote, velocity=127, time=tickDiff))
            pString = f"| note_off channel=0 note={mNote} velocity=127 time={tickDiff})"
            logger.debug (f"{pString:76} |")
            tickDiff = 0
        prevKey = key + _8th
    
    # Finished generating all notes, end the track and clean up
    pString = f"| MetaMessage('end_of_track', time=0)"
    logger.debug (f"{pString:76} |")
    logger.debug ("------------------------------------------------------------------------------")
    oFile.save(oFileName)
    logger.info (f"Successfully generated quantized MIDI file: {oFileName}")

# This function creates tabulature using the generated MIDI file from generateMIDI
def notesToTabs(noteTime, tpb, tempo, noteTable, maxFWidth):
    # Creates a list of tabs to play up to the very end of the generated MIDI file
    # These tabs are initialized to -1, meaning no note being played, and get filled in throughout the function
    logger.info ("Generating guitar tabulature from MIDI file")
    lastNT = list(noteTime.keys())[-1]
    tabs = [[-1,-1,-1,-1,-1,-1] for i in range(0,lastNT+1,_8th)]
    playableStrings = [True * 6]
    
    # Takes eighth steps up to the very last eighth of the song. If no strings are to be played (as per the keys in noteTime), then skip, otherwise go through the else block
    for i in range (0, lastNT + 1, _8th):
        chordTime = i
        chordTick = chordTime//_8th
        if i not in noteTime:
            pass
        else:
            # This else block attempts to find a way to play all the notes on the current tick
            logging.debug ("------------------------------------------------------------------------------")
            logging.debug (f"Found a note to play at absolute tick: {chordTime}")
            playableStrings = [True, True, True, True, True, True]
            notesToPlay = noteTime[chordTime]
            possFingering = {}
            for index, value in enumerate(notesToPlay):
                possFingering[value] = []
            
            # Make sure that the current note is actually playable with the current tuning/capo/etc.
            for note in notesToPlay:
                try:
                    possFingering[note] = noteTable[note]
                except:
                    print (f"Found an unplayable note: {note}; Omitting from tab")
                    logging.info (f"Found an unplayable note: {note} at {chordTime}; Omitting from tab")

            # Takes the Cartesian product (all possible combinations) of all notes to play and all of their possible fingerings/ways to play them
            # For each permutation, check if it's already been covered (in a playable way)
            # If not, check if all the notes using the current permutation is playable (according to finger width, strings available, etc.)
            # If so add it to the tab and go to the next chord to play
            # If not, check the next permutation after resetting
            perms = [dict(zip(possFingering, v)) for v in itertools.product(*possFingering.values())]
            for possChord in perms:
                # For some reason, trying to find a way to play a tab that was already generated, skip
                if (tabs [chordTick] != [-1,-1,-1,-1,-1,-1]):
                    logging.debug (f"Already found a playable chord; going to the next chord to play")
                    break
                lowestFinger = 999
                highestFinger = -1
                noteCount = 0
                for midiNote, noteChoice in possChord.items():
                    # The encoding is as follows (more information in notes.py:
                    # 301 -> 3 01 -> 1st fret on the 3rd string
                    noteCString_i = (noteChoice // 100) - 1
                    noteCFret = noteChoice % 100
                    
                    # The current permutation plays multiple notes on the same string; Invalid
                    if not playableStrings[noteCString_i]:
                        playableStrings = [True, True, True, True, True, True]
                        tabs [chordTick] = [-1,-1,-1,-1,-1,-1]
                        noteCount = 0
                        logging.debug (f"REJECTED - Possible chord: {str(possChord):30} Conflicting strings")
                        break

                    if noteCFret != 0:
                        lowestFinger = min(noteCFret, lowestFinger)
                        highestFinger = max(noteCFret, highestFinger)
                        # The current permutation plays notes that are too far apart; Invalid
                        if (highestFinger - lowestFinger > maxFWidth):
                            noteCount = 0
                            playableStrings = [True, True, True, True, True, True]
                            tabs [chordTick] = [-1,-1,-1,-1,-1,-1]
                            logging.debug (f"REJECTED - Possible chord: {str(possChord):30} Finger Width too small")
                            break
                    
                    # Atleast for now, all seen notes are playable simultaneously
                    tabs [chordTick][noteCString_i] = noteCFret
                    playableStrings[noteCString_i] = False
                    noteCount += 1

                    # The tab is only fully accepted when the amount of notes to play == amount of string played
                    if (noteCount >= len(possChord.items())):
                        logging.debug (f"ACCEPTED - Possible chord: {str(possChord):30}")
                        logging.debug (f"Generated tab as follows:")
                        tp.tabPrettyPrintChord(tabs[chordTick])
                        break
    logging.debug ("------------------------------------------------------------------------------")
    logger.info ("Successfully generated guitar tabulature")
    return tabs

# This function "cleans" the input MIDI file. Note that behavior is unexpected for multi-track MIDIs
# Currently, it is limited to checking for when notes are triggered and mapping each note to the nearest 8th. The main return value is the noteTime table
# This is a dictionary with the keys as the absolute time (in ticks), and value as the notes to play on that tick
# Future plans include:
# 1. Checking when notes are too close to each other and filtering them out, as they were likely false triggers
# 2. Comparing note velocities and making it s.t. notes too qutie from the current loudest are filtered out
def quantizeMIDI (iFileName):
    logger.info ("Quantize input MIDI file")

    tempo = -1
    tpb = -1
    noteTime = col.OrderedDict()
    currNotes = {}

    # Tries to open the specified MIDI file
    try:
        inMIDI = m.MidiFile(f"{iFileName}", clip = True)
    except FileNotFoundError:
        logger.error (f"Unable to find specified file: {iFileName}")
        print (f"Error - Unable to find specified file: {iFileName}")
        exit()
    except:
        logger.error (f"Unknown error occured while opening the specified MIDI file")
        print ("Unknown error occured while opening the specified MIDI file")
        exit()

    for i, track in enumerate(inMIDI.tracks):
        # Initializes some variables based on the input
        absTicks = 0
        tpb = inMIDI.ticks_per_beat
        global _8th
        _8th = int((tpb/8))
        global _16th
        _16th = int((tpb/16))
        logger.info (f"ticks_per_beat: {tpb}")

        # Each MIDI file consists of several tracks, each with several messages. In this case, we mostly only care about note_on except for a couple of exceptions
        for message in track:
            absTicks += message.time
            if (message.is_meta) and tempo < 0 and message.type == "set_tempo":
                tempo = message.tempo
                logger.info (f"Tempo set to: {tempo}")
            
            # For every note_on message we have, we change the timing to the nearest eight note according to the variables set earlier
            # After finding the nearest eight, add it to the noteTime dictionary
            if (message.type == "note_on"):
                # Default tempo
                if (tempo < 0):
                    tempo = 500000
                if absTicks%_8th <= _16th:
                    m_absTicks = int((absTicks//_8th)*_8th)
                else:
                    m_absTicks = int(math.ceil(absTicks//_8th)*_8th)
                currNotes = noteTime.setdefault(m_absTicks, [])
                currNotes.append(message.note)
                noteTime[m_absTicks] = currNotes
    logger.debug ("The input MIDI file has generated the following table")
    logger.debug ("|  Absolute ticks   |   Notes to Play (MIDI)   |")
    for time, value in noteTime.items():
        valString = str(value)
        logger.debug (f"|{time : 17}  |  {valString:24}|")
    logger.info ("MIDI file successfully quantized")

    return noteTime, tpb, tempo