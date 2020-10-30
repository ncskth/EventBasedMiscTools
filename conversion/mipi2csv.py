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
    This function prints 8 nibbles of a 32-bit integer
'''
def log_nibbles_b(a):

    nibble1 = format((a & int.from_bytes(b'\x00\x00\x00\xF0',"little"))>>28, '#06b')
    nibble2 = format((a & int.from_bytes(b'\x00\x00\x00\x0F',"little"))>>24, '#06b')
    nibble3 = format((a & int.from_bytes(b'\x00\x00\xF0\x00',"little"))>>20, '#06b')
    nibble4 = format((a & int.from_bytes(b'\x00\x00\x0F\x00',"little"))>>16, '#06b')
    nibble5 = format((a & int.from_bytes(b'\x00\xF0\x00\x00',"little"))>>12, '#06b')
    nibble6 = format((a & int.from_bytes(b'\x00\x0F\x00\x00',"little"))>>8, '#06b')
    nibble7 = format((a & int.from_bytes(b'\xF0\x00\x00\x00',"little"))>>4, '#06b')
    nibble8 = format((a & int.from_bytes(b'\x0F\x00\x00\x00',"little"))>>0, '#06b')

    print("Original: " + str(a) + " --> " + nibble1 + " " + nibble2 +
              " " + nibble3 + " " + nibble4 + " " + nibble5 + " " + nibble6 +
              " " + nibble7 + " " + nibble8 + "\n")
    return a


'''
    This function prints 8 nibbles of a 32-bit integer
'''
def log_nibbles_h(a):

    nibble1 = format((a & int.from_bytes(b'\x00\x00\x00\xF0',"little"))>>28, '#01x')
    nibble2 = format((a & int.from_bytes(b'\x00\x00\x00\x0F',"little"))>>24, '#01x')
    nibble3 = format((a & int.from_bytes(b'\x00\x00\xF0\x00',"little"))>>20, '#01x')
    nibble4 = format((a & int.from_bytes(b'\x00\x00\x0F\x00',"little"))>>16, '#01x')
    nibble5 = format((a & int.from_bytes(b'\x00\xF0\x00\x00',"little"))>>12, '#01x')
    nibble6 = format((a & int.from_bytes(b'\x00\x0F\x00\x00',"little"))>>8, '#01x')
    nibble7 = format((a & int.from_bytes(b'\xF0\x00\x00\x00',"little"))>>4, '#01x')
    nibble8 = format((a & int.from_bytes(b'\x0F\x00\x00\x00',"little"))>>0, '#01x')

    print(nibble7 + " " + nibble8)
    print(nibble5 + " " + nibble6)
    print(nibble3 + " " + nibble4)
    print(nibble1 + " " + nibble2)

    return a

'''
This function reads a *.mipi file, decodes it and writes a *.csv file
'''
def convert(argv, flag=False, n=-1):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"i:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('mipi2csv.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    start = time.time()

    ifile = open(inputfile, "rb")
    try:

        print("\n")
        print("HEADER")

        for i in range(3):
        #     # Read first byte of current line without advancing position
        #     pos = ifile.tell()
            line = ifile.read(4)
            log_nibbles_h(int.from_bytes(line, "little"))

        #Package Length
        print("Package Length")
        line = ifile.read(4)
        a = log_nibbles_b(int.from_bytes(line, "little"))

        c = 0
        while True:

            word = ifile.read(4)
            if word == b'':
                print(str(c) + " package buffers were found")
                break

            a = int.from_bytes(word, "little")
            if a == 357001:
                c += 1
                pos = ifile.tell()
                print("\n\n\nPackage Length at: " + str(pos))
                ifile.read(a)
                ifile.read(8)
                word = ifile.read(4)
                a = int.from_bytes(word, "little")
                print("IMU count: " + str(a))
                ifile.seek(pos)



# 572,551,0
# 573,556,0
# 574,540,10
# 574,572,10
# 574,573,10
# 575,540,10
# 575,544,10
# 575,547,10
# 575,571,10
# 575,582,10



        #
        #
        # #Package Length
        # print("Package Length")
        # line = ifile.read(4)
        # a = log_nibbles_b(int.from_bytes(line, "little"))
        #
        # # Package Buffer
        # line = ifile.read(a)
        #
        # #Package Timestamp
        # line = ifile.read(8)
        #
        # #IMU count
        # print("IMU count")
        # line = ifile.read(4)
        # a = log_nibbles_b(int.from_bytes(line, "little"))
        #
        # #IMU data
        # line = ifile.read(a*28)
        #
        # #Package Length
        # print("Package Length")
        # line = ifile.read(4)
        # a = log_nibbles_b(int.from_bytes(line, "little"))


        print("\n")


    finally:
        ifile.close()


    stop = time.time()

    elapsed = stop-start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":
    convert(sys.argv[1:])
