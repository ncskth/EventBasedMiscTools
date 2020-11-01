#!/usr/bin/python

from dv import AedatFile
import sys, getopt
import pdb
import time


'''
    To parse all the events:
        python3 parse_aedat4.py -i filename.raw -n -1
    To parse 23 the events:
        python3 parse_aedat4.py -i filename.raw -n 23
'''

def getInputs(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"i:n:",["ifile=","nevents="])
    except getopt.GetoptError:
        print('parse_aedat4.py -i <inputfile> -n <nb_events>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-n", "--nevents"):
            nb_events = int(arg)
    return inputfile, nb_events

def getNextRow(inputfile):

    with AedatFile(inputfile) as ifile:
        # loop through the "events" stream
        for e in ifile['events']:
            t = e.timestamp
            x = e.x
            y = e.y
            p = int(e.polarity)
            yield(t,x,y,p)


'''
    Dummy function that prints out the first k events from the input file
'''
def doSomething(t,x,y,p, line_count):
        k = 5 # max number of events to print out
        if (line_count <= k):
            print(str(t) + '|' + str(x) + '|' + str(y) + '|' + str(p))
        elif (line_count == k+1):
            print("...")


if __name__ == "__main__":


    inputfile, nb_events = getInputs(sys.argv[1:])

    start = time.time()

    line_count = 0
    for t,x,y,p in getNextRow(inputfile):
        line_count += 1

        doSomething(t,x,y,p, line_count)

        # Check if enough events have been parsed
        if (nb_events > 0) and (line_count > nb_events):
            # Stop parsing since nb_events reached
            break

    stop = time.time()

    elapsed = stop-start
    print("Parser took: " + str(int(elapsed)) + " seconds.")
