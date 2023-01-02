import logging

logger = logging.getLogger(__name__)

# These functions pretty print tabulature from the inputs;
def tabPrettyPrint (neck, oFile):
    logging.info ("Pretty Printing tabulature")
    oString = [ "" for _ in range(6) ]
    bars = 0

    # 
    try:
        with open (oFile, "w+") as tabFile:
            for index, chord in enumerate(neck):
                for string, fret in enumerate(chord):
                    if fret < 0:
                        oString[string] += "--"
                    elif fret < 10:
                        oString[string] += f"-{fret}"
                    else:
                        oString[string] += f"{fret}"
                # Draw a set of newlines
                if (index % 8) == 7:
                    if bars <= 2:
                        bars += 1
                        for i in range (-1, -len(oString)-1, -1):
                            oString[i] += "|"
                    else:
                        for i in range (-1, -len(oString)-1, -1):
                            tabFile.write (oString[i] + "|\n")
                        oString = [ "" for _ in range(6) ]
                        bars = 0
                        tabFile.write ("\n")
            for i in range (-1, -len(oString)-1, -1):
                tabFile.write (oString[i] + "|\n")
            tabFile.write ("\n")
            logging.info (f"Successfully printed guitar tabulature to: {oFile}")
    except:
        logging.error (f"Unable to open specified output file {oFile}")

def tabPrettyPrintChord (neck):
    oString = [ "" for _ in range(6) ]
    for string, fret in enumerate(neck):
        if fret < 0:
            oString[string] += "--"
        elif fret < 10:
            oString[string] += f"-{fret}"
        else:
            oString[string] += f"{fret}"
    for i in range (-1, -len(oString)-1, -1):
        logging.debug(f"{oString[i]}")