#!/usr/bin/python

import sys, getopt
import time
import numpy as np
import csv
from struct import *
import sys
import os
import pdb


binatt = ["data_type", "loopA_mode", "loopB_mode", "loopC_mode", "event_data_format", "hour", "minute", "second", "package_count"]

'''
    This function prints 8 nibbles of a 32-bit integer
'''
def log_8_nibbles_b(a):

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
def log_8_nibbles_h(a):

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
    This function prints 2 nibbles of a 32-bit integer
'''
def log_2_nibbles_b(a):
    nibble1 = format((a & int.from_bytes(b'\xF0\x00\x00\x00',"little"))>>4, '#06b')
    nibble2 = format((a & int.from_bytes(b'\x0F\x00\x00\x00',"little"))>>0, '#06b')

    print("Original: " + str(a) + " --> " + nibble1 + " " + nibble2 + "\n")

    return a

'''
    This function prints 2 nibbles of a 32-bit integer
'''
def log_2_nibbles_h(a):
    nibble1 = format((a & int.from_bytes(b'\xF0\x00\x00\x00',"little"))>>4, '#01x')
    nibble2 = format((a & int.from_bytes(b'\x0F\x00\x00\x00',"little"))>>0, '#01x')

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

        for i in range(8):
            print(binatt[i])
            line = ifile.read(1)
            log_2_nibbles_b(int.from_bytes(line, "little"))
            print("\n")

        print("package_count")
        line = ifile.read(4)
        log_8_nibbles_b(int.from_bytes(line, "little"))
        print("\n")

        print("\n")
        print("DATA")


        row = -1
        col = -1
        t = -1

        mat = np.zeros((800,1280), dtype = np.int8)

        stopLoop = False

        with open(outputfile, 'w') as ofile:

            csvwriter = csv.writer(ofile, delimiter=',')

            while not stopLoop:

                line = ifile.read(4)
                if line == b'':
                        break

                # Reading Package Buffer
                a = int.from_bytes(line, "little")
                line = ifile.read(a)

                for i in range(int(a/7)):

                    if stopLoop:
                        break

                    p_a_1 = (line[i*7+0])<<6
                    p_a_2 = (line[i*7+4] & (int.from_bytes(b'\x3F',"little")))
                    p_b_1 = (line[i*7+1])<<6
                    p_b_2 = (line[i*7+5] & (int.from_bytes(b'\x0F',"little")))<<2
                    p_b_3 = (line[i*7+4] & (int.from_bytes(b'\xC0',"little")))>>6
                    p_c_1 = (line[i*7+2])<<6
                    p_c_2 = (line[i*7+6] & (int.from_bytes(b'\x03',"little")))<<4
                    p_c_3 = (line[i*7+5] & (int.from_bytes(b'\xF0',"little")))>>4
                    p_d_1 = (line[i*7+3])<<6
                    p_d_2 = (line[i*7+6] & (int.from_bytes(b'\xFC',"little")))>>2

                    p_a = p_a_1 + p_a_2
                    p_b = p_b_1 + p_b_2 + p_b_3
                    p_c = p_c_1 + p_c_2 + p_c_3
                    p_d = p_d_1 + p_d_2

                    p_x = [p_a, p_b, p_c, p_d]

                    for p_x in [p_a, p_b, p_c, p_d]:
                        id_x = (p_x & int.from_bytes(b'\x03\x00',"little"))

                        # Timestamp
                        if id_x == 3:
                            if t < 0:
                                t = 0
                                old_t = (p_x >> 2)
                            else:
                                # pdb.set_trace()
                                t = t + max(0,(p_x >> 2)-old_t)
                                old_t = (p_x >> 2)

                        # Row
                        if id_x == 2:
                            row = (p_x >> 4)

                        # Column
                        if id_x == 1:
                            col = (p_x >> 3)
                            pol = 1-mat[row,col]
                            mat[row,col] = pol
                            csvwriter.writerow([t] + [col] + [row] + [pol])

                # Package Timestamp
                line = ifile.read(8)

                # IMU count
                line = ifile.read(4)
                a = int.from_bytes(line, "little")

                # Reading IMU Data
                # line = ifile.read(a*32)
                pos = ifile.tell()
                ifile.seek(pos+a*32)

            print("\n")


    finally:
        ifile.close()


    stop = time.time()

    elapsed = stop-start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":
    convert(sys.argv[1:])
