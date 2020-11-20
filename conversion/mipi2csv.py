#!/usr/bin/python

import sys, getopt
import time
import numpy as np
import csv
from struct import *
import sys
import os
import pdb


binatt = [
    "data_type",
    "loopA_mode",
    "loopB_mode",
    "loopC_mode",
    "event_data_format",
    "hour",
    "minute",
    "second",
    "package_count",
]

"""
This function reads a *.mipi file, decodes it and writes a *.csv file
"""


def convert(argv, flag=False, n=-1):
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "i:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("mipi2csv.py -i <inputfile> -o <outputfile>")
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

        # uint8_t x 8
        for i in range(8):
            print(binatt[i])
            line = ifile.read(1)
        # uint32_t
        print("package_count")
        line = ifile.read(4)

        print("\n")
        print("DATA")
        print("...")

        row = -1
        col = -1
        t = -1
        mat = np.zeros((800, 1280), dtype=np.int8)

        stopLoop = False

        with open(outputfile, "w") as ofile:

            csvwriter = csv.writer(ofile, delimiter=",")

            while True:

                line = ifile.read(4)
                if line == b"":
                    break

                # Reading Package Buffer
                a = int.from_bytes(line, "little")
                line = ifile.read(a)

                for i in range(int(a / 7)):

                    # p_a_1 = (line[i*7+0])<<6
                    # p_a_2 = (line[i*7+4] & (int.from_bytes(b'\x3F',"little")))
                    # p_b_1 = (line[i*7+1])<<6
                    # p_b_2 = (line[i*7+5] & (int.from_bytes(b'\x0F',"little")))<<2
                    # p_b_3 = (line[i*7+4] & (int.from_bytes(b'\xC0',"little")))>>6
                    # p_c_1 = (line[i*7+2])<<6
                    # p_c_2 = (line[i*7+6] & (int.from_bytes(b'\x03',"little")))<<4
                    # p_c_3 = (line[i*7+5] & (int.from_bytes(b'\xF0',"little")))>>4
                    # p_d_1 = (line[i*7+3])<<6
                    # p_d_2 = (line[i*7+6] & (int.from_bytes(b'\xFC',"little")))>>2
                    #
                    # p_a = p_a_1 + p_a_2
                    # p_b = p_b_1 + p_b_2 + p_b_3
                    # p_c = p_c_1 + p_c_2 + p_c_3
                    # p_d = p_d_1 + p_d_2

                    p_a = ((line[i * 7 + 0]) << 6) + (
                        (line[i * 7 + 4] & (int.from_bytes(b"\x3F", "little")))
                    )
                    p_b = (
                        ((line[i * 7 + 1]) << 6)
                        + ((line[i * 7 + 5] & (int.from_bytes(b"\x0F", "little"))) << 2)
                        + ((line[i * 7 + 4] & (int.from_bytes(b"\xC0", "little"))) >> 6)
                    )
                    p_c = (
                        ((line[i * 7 + 2]) << 6)
                        + ((line[i * 7 + 6] & (int.from_bytes(b"\x03", "little"))) << 4)
                        + ((line[i * 7 + 5] & (int.from_bytes(b"\xF0", "little"))) >> 4)
                    )
                    p_d = ((line[i * 7 + 3]) << 6) + (
                        (line[i * 7 + 6] & (int.from_bytes(b"\xFC", "little"))) >> 2
                    )

                    p_x = [p_a, p_b, p_c, p_d]

                    for p_x in [p_a, p_b, p_c, p_d]:
                        id_x = p_x & int.from_bytes(b"\x03\x00", "little")

                        # Timestamp
                        if id_x == 3:
                            if t < 0:
                                t = 0
                                old_t = p_x >> 2
                            else:
                                # pdb.set_trace()
                                t = t + max(0, (p_x >> 2) - old_t)
                                old_t = p_x >> 2

                        # Row
                        if id_x == 2:
                            row = p_x >> 4

                        # Column
                        if id_x == 1:
                            col = p_x >> 3
                            pol = 1 - mat[row, col]
                            mat[row, col] = pol
                            csvwriter.writerow([t] + [col] + [row] + [pol])

                # Package Timestamp
                line = ifile.read(8)

                # IMU count
                line = ifile.read(4)
                a = int.from_bytes(line, "little")

                # Skipping IMU Data
                pos = ifile.tell()
                ifile.seek(pos + a * 32)

            print("\n")

    finally:
        ifile.close()

    stop = time.time()

    elapsed = stop - start
    print("The conversion took: " + str(int(elapsed)) + " seconds.")


if __name__ == "__main__":
    convert(sys.argv[1:])
