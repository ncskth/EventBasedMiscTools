#!/usr/bin/python

from dv import AedatFile
import csv

"""
    This generator yields an event using timestamp (t), pixel coordinates (x,y) and polarity (p)
"""
def getNextEvent(inputfile):

    # This block corresponds to the *.csv parser
    if ".csv" in inputfile:
        print(".csv !!!")
        with open(inputfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                t = int(row[0])  # timestamp
                x = int(row[1])  # pixel's x-coordinate
                y = int(row[2])  # pixel's y-coordinate
                p = int(row[3])  # event polarity
                yield (t, x, y, p)

    # This block corresponds to the *.aedat4 parser
    if ".aedat4" in inputfile:
        print(".aedat4 !!!")
        with AedatFile(inputfile) as ifile:
            # loop through the "events" stream
            for e in ifile["events"]:
                t = e.timestamp
                x = e.x
                y = e.y
                p = int(e.polarity)
                yield (t, x, y, p)

    # This block corresponds to the *.raw parser
    if ".raw" in inputfile:
        print(".raw !!!")

        t_base = 0
        header = True

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

        with open(inputfile, "rb") as ifile:

            while header:
                # Read first byte of current line without advancing position
                pos = ifile.tell()
                line = ifile.read(1)
                ifile.seek(pos)
                # Header lines start with '%'
                if line == b"%":
                    line = ifile.readline()
                else:
                    # Header is over (no '%' found)
                    header = False
                    break

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
