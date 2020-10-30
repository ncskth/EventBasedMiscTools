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

global t_base
t_base = 0

'''
    This function prints 8 nibbles of a 32-bit integer
'''
def log_nibbles(a):

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

    # Masks to decode events
    mask_e_type = b'\x00\x00\x00\xF0'
    mask_t_base = b'\x00\x00\xC0\x0F'
    mask_t_high = b'\xFF\xFF\xFF\x0F'
    mask_x_pixel = b'\x00\xF8\x3F\x00'
    mask_y_pixel = b'\xFF\x07\x00\x00'

    # Bit Shifters to decode events
    shift_e_type = 28
    shift_x_pixel = 11
    shift_y_pixel = 0
    shift_t_base = 22
    shift_t_high = 6

    # Current time base
    global t_base


    ifile = open(inputfile, "rb")
    try:

        print("\n")
        print("HEADER")

        while True:
            # Read first byte of current line without advancing position
            pos = ifile.tell()
            line = ifile.read(1)
            ifile.seek(pos)
            # Header lines start with '%'
            if line == b'%':
                line = ifile.readline()
                print(line)
            else:
                # Header is over (no '%' found)
                break
        print("\n")

        print("DATA:")

        with open(outputfile, 'w') as ofile:

            csvwriter = csv.writer(ofile, delimiter=',')

            c = 0
            e_array = []
            while True:

                word = ifile.read(4)
                if word == b'':
                    break

                a = int.from_bytes(word, "little")
                if flag:
                    log_nibbles(a)

                p1 = (a & int.from_bytes(mask_e_type,"little")) >> shift_e_type

                # Decode CD_OFF + CD_ON
                if (p1==1) or (p1==0):

                    p2 = (a & int.from_bytes(mask_t_base,"little")) >> shift_t_base
                    p3 = (a & int.from_bytes(mask_x_pixel,"little")) >> shift_x_pixel
                    p4 = (a & int.from_bytes(mask_y_pixel,"little")) >> shift_y_pixel

                    if t_base != 0:
                        # csvwriter.writerow([p3] + [p4] + [p1] + [t_base+p2])
                        csvwriter.writerow([t_base+p2] + [p3] + [p4] + [p1])
                        c += 1
                    if(c==n):
                        break

                # Decode EVT_TIME_HIGH
                elif (p1 == 8):
                    p2 = (a & int.from_bytes(mask_t_high,"little")) << shift_t_high
                    t_base = p2

        os.system("head -5 %s" %(ofile.name))
        print("...")
        print("...")
        print("...")
        os.system("tail -5 %s" %(ofile.name))
        print("\n")

        print(str(c) + " events were extraced\n\n")


    finally:
        ifile.close()


    stop = time.time()

    elapsed = stop-start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":
    convert(sys.argv[1:])
