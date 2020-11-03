#!/usr/bin/python

import sys, getopt
from dv import AedatFile
import scipy.io as sio
import numpy
import time
import csv


def convert(argv):
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "i:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("aedat2csv.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    start = time.time()

    with AedatFile(inputfile) as ifile, open(outputfile, "w", newline="") as ofile:

        # events will be a named numpy array
        events = numpy.hstack([packet for packet in ifile["events"].numpy()])

        # Access information of all events by type
        t, x, y, p = events["timestamp"], events["x"], events["y"], events["polarity"]

        numpy.savetxt(
            outputfile, numpy.transpose([t, x, y, p]), fmt="%ld", delimiter=","
        )

    stop = time.time()

    elapsed = stop - start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":

    convert(sys.argv[1:])
