#!/usr/bin/python

import sys, getopt
import scipy.io as sio
import numpy as np
import time
import csv
from struct import *
import sys
import os
import pdb


'''
This function reads a *.raw file, decodes it and writes a *.csv file
'''
def convert(argv, flag=False, n=-1):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"i:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('raw2csv.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    start = time.time()


    with open(inputfile, newline='') as ifile:
        csvreader = csv.reader(ifile, delimiter=',')
        c = 0
        for line in csvreader:
            print(line)
            c += 1
            if(c>9):
                break


    stop = time.time()

    elapsed = stop-start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":
    convert(sys.argv[1:])
