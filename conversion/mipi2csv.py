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

        #Package Length
        count = 0
        while True:

            line = ifile.read(4)
            if line == b'':
                    break
            else:
                count +=1
                print("Package #" + str(count))

            print("Package Length")
            a = log_8_nibbles_b(int.from_bytes(line, "little"))

            # Reading Package Buffer
            line = ifile.read(a)

            for i in range(int(a/7)):
                p_a = line[i*7+0]<<6 + 0 # E[5:0]
                p_b = line[i*7+1]<<6 + 0 # F[3:0] + E[7:6]
                p_c = line[i*7+2]<<6 + 0 # G[1:0] + F[7:4]
                p_d = line[i*7+3]<<6 + 0 # G[7:2]
                # format(p_a, '#01x')
                pdb.set_trace()


            line = ifile.read(8)
            print("Timestamp")
            a = log_8_nibbles_b(int.from_bytes(line, "little"))


            line = ifile.read(4)
            print("IMU count")
            a = log_8_nibbles_b(int.from_bytes(line, "little"))

            # Reading IMU Data
            line = ifile.read(a*32)




        # c = 0
        # k = 1
        # while True:
        #     pos = ifile.tell()
        #     line = ifile.read(4)
        #     if line == b'':
        #         break
        #     a = int.from_bytes(line, "little")
        #     c += 1
        #     if a == 357001:
        #         print("c = " + str(c) + "**************************")
        #         c = 0
        #         k += 1
        #         print("k = " + str(k) + ": a = " + str(a) + " at pos = " + str(pos))
        #         ifile.read(a)
        #         print("Timestamp")
        #         line = ifile.read(8)
        #         a = log_8_nibbles_b(int.from_bytes(line, "little"))
        #         print("@@@" + str(ifile.tell()))
        #         print("IMU count")
        #         line = ifile.read(4)
        #         a = log_8_nibbles_b(int.from_bytes(line, "little"))
        #     else:
        #         ifile.seek(pos)
        #         ifile.read(1)
        #         c += 1



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
        # a = log_8_nibbles_b(int.from_bytes(line, "little"))
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
        # a = log_8_nibbles_b(int.from_bytes(line, "little"))
        #
        # #IMU data
        # line = ifile.read(a*28)
        #
        # #Package Length
        # print("Package Length")
        # line = ifile.read(4)
        # a = log_8_nibbles_b(int.from_bytes(line, "little"))


        print("\n")


    finally:
        ifile.close()


    stop = time.time()

    elapsed = stop-start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":
    convert(sys.argv[1:])
