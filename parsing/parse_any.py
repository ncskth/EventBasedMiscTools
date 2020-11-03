#!/usr/bin/python

from dv import AedatFile
import sys, getopt
import time
import csv

# Masks to decode events
mask_e_type = b"\x00\x00\x00\xF0"
mask_t_base = b"\x00\x00\xC0\x0F"
mask_t_high = b"\xFF\xFF\xFF\x0F"
mask_x_pixel = b"\x00\xF8\x3F\x00"
mask_y_pixel = b"\xFF\x07\x00\x00"

# Bit Shifters to decode events
shift_e_type = 28
shift_x_pixel = 11
shift_y_pixel = 0
shift_t_base = 22
shift_t_high = 6

global t_base
t_base = 0
global header
header = True
global line_count
line_count = 0

"""
    To parse all the events in a *.aedat4 file:
        python3 parse_any.py -i filename.aedat4 -n -1
    To parse 23 the events in a *.raw file:
        python3 parse_any.py -i filename.raw -n 23
"""


def getInputs(argv):
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "i:n:", ["ifile=", "nevents="])
    except getopt.GetoptError:
        print("parse_any.py -i <inputfile> -n <nb_events>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-n", "--nevents"):
            nb_events = int(arg)
    return inputfile, nb_events


"""
    This generator yields an event using timestamp (t), pixel coordinates (x,y) and polarity (p)
"""


def getNextEvent(inputfile):

    # This block corresponds to the *.csv parser
    if ".csv" in inputfile:
        print(".csv !!!")
        with open(inputfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                t = int(row[0])  # timestamp
                x = int(row[1])  # pixel's x-coordinate
                y = int(row[2])  # pixel's y-coordinate
                p = int(row[3])  # event polarity
                yield (t, x, y, p)

    # This block corresponds to the *.aedat4 parser
    if ".aedat4" in inputfile:
        print(".aedat4 !!!")
        with AedatFile(inputfile) as ifile:
            # loop through the "events" stream
            for e in ifile["events"]:
                t = e.timestamp
                x = e.x
                y = e.y
                p = int(e.polarity)
                yield (t, x, y, p)

    # This block corresponds to the *.raw parser
    if ".raw" in inputfile:
        print(".raw !!!")
        global t_base
        global header

        with open(inputfile, "rb") as ifile:

            while header:
                # Read first byte of current line without advancing position
                pos = ifile.tell()
                line = ifile.read(1)
                ifile.seek(pos)
                # Header lines start with '%'
                if line == b"%":
                    line = ifile.readline()
                else:
                    # Header is over (no '%' found)
                    header = False
                    break

            c = 0
            e_array = []

            stop = False
            while True:
                word = ifile.read(4)
                if word == b"":
                    break

                a = int.from_bytes(word, "little")

                p1 = (a & int.from_bytes(mask_e_type, "little")) >> shift_e_type

                # Decode CD_OFF + CD_ON
                if (p1 == 1) or (p1 == 0):

                    p2 = (a & int.from_bytes(mask_t_base, "little")) >> shift_t_base
                    p3 = (a & int.from_bytes(mask_x_pixel, "little")) >> shift_x_pixel
                    p4 = (a & int.from_bytes(mask_y_pixel, "little")) >> shift_y_pixel

                    if t_base != 0:
                        t = t_base + p2
                        x = p3
                        y = p4
                        p = p1
                        c += 1
                        yield (t, x, y, p)

                # Decode EVT_TIME_HIGH
                elif p1 == 8:
                    p2 = (a & int.from_bytes(mask_t_high, "little")) << shift_t_high
                    t_base = p2


"""
    This functions returns 'True' when the expected number of events to parse is reached
"""


def stopParsing(nb_events):

    global line_count
    # Check if enough events have been parsed
    if (nb_events > 0) and (line_count > nb_events):
        # Stop parsing since nb_events reached
        return True
    else:
        return False


"""
    Dummy function that prints out the first k events from the input file
"""


def doSomething(t, x, y, p):
    global line_count
    k = 5  # max number of events to print out
    line_count += 1
    if line_count <= k:
        print(str(t) + "|" + str(x) + "|" + str(y) + "|" + str(p))
    elif line_count == k + 1:
        print("...")


if __name__ == "__main__":

    inputfile, nb_events = getInputs(sys.argv[1:])
    start = time.time()

    # This loop
    for t, x, y, p in getNextEvent(inputfile):

        doSomething(t, x, y, p)

        if stopParsing(nb_events):
            break

    stop = time.time()
    elapsed = stop - start
    print("Parser took: " + str(int(elapsed)) + " seconds.")
