import sys, getopt
import time
from parser import getNextEvent

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
