import sys, getopt
import pdb
import time

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
global header
t_base = 0
header = True

"""
    To parse all the events:
        python3 parse_raw.py -i filename.raw -n -1
    To parse 23 the events:
        python3 parse_raw.py -i filename.raw -n 23
"""


def getInputs(argv):
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "i:n:", ["ifile=", "nevents="])
    except getopt.GetoptError:
        print("parse_raw.py -i <inputfile> -n <nb_events>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-n", "--nevents"):
            nb_events = int(arg)
    return inputfile, nb_events


def getNextRow(inputfile):

    # Current time base
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
                print(line)
            else:
                # Header is over (no '%' found)
                header = False
                break
        print("\n")

        print("DATA:")

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
    Dummy function that prints out the first k events from the input file
"""


def doSomething(t, x, y, p, line_count):
    k = 5  # max number of events to print out
    if line_count <= k:
        print(str(t) + "|" + str(x) + "|" + str(y) + "|" + str(p))
    elif line_count == k + 1:
        print("...")


if __name__ == "__main__":

    inputfile, nb_events = getInputs(sys.argv[1:])

    start = time.time()

    line_count = 0
    for t, x, y, p in getNextRow(inputfile):
        line_count += 1

        doSomething(t, x, y, p, line_count)
        # print(str(line_count) + ": " + str(t) + '|' + str(x) + '|' + str(y) + '|' + str(p))

        # Check if enough events have been parsed
        if (nb_events > 0) and (line_count > nb_events):
            # Stop parsing since nb_events reached
            break

    stop = time.time()

    elapsed = stop - start
    print("Parser took: " + str(int(elapsed)) + " seconds.")
