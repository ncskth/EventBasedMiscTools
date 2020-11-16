import sys, getopt
import pdb
import time
import numpy as np

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
    To parse all the events:
        python3 parse_mipi.py -i filename.raw -n -1
    To parse 23 the events:
        python3 parse_mipi.py -i filename.raw -n 23
"""


def getInputs(argv):
    inputfile = ""
    try:
        opts, args = getopt.getopt(argv, "i:n:", ["ifile=", "nevents="])
    except getopt.GetoptError:
        print("parse_mipi.py -i <inputfile> -n <nb_events>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-n", "--nevents"):
            nb_events = int(arg)
    return inputfile, nb_events


def getNextRow(inputfile):

    header = True

    with open(inputfile, "rb") as ifile:

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

        while True:
            word = ifile.read(4)
            if word == b"":
                break

            # Reading Package Buffer
            a = int.from_bytes(line, "little")
            line = ifile.read(a)

            for i in range(int(a / 7)):

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
                        # csvwriter.writerow([t] + [col] + [row] + [pol])
                        yield (t, col, row, pol)

            # Package Timestamp
            line = ifile.read(8)

            # IMU count
            line = ifile.read(4)
            a = int.from_bytes(line, "little")

            # Skipping IMU Data
            pos = ifile.tell()
            ifile.seek(pos + a * 32)


"""
    Dummy function that prints out the first k events from the input file
"""


def doSomething(t, x, y, p, line_count):
    k = 50  # max number of events to print out
    if line_count <= k:
        print(str(t) + "|" + str(x) + "|" + str(y) + "|" + str(p))
    elif line_count == k + 1:
        print("...")


if __name__ == "__main__":

    inputfile, nb_events = getInputs(sys.argv[1:])

    start = time.time()

    line_count = 0
    for t, x, y, p in getNextRow(inputfile):
        line_count += 1

        doSomething(t, x, y, p, line_count)
        # print(str(line_count) + ": " + str(t) + '|' + str(x) + '|' + str(y) + '|' + str(p))

        # Check if enough events have been parsed
        if (nb_events > 0) and (line_count > nb_events):
            # Stop parsing since nb_events reached
            break

    stop = time.time()

    elapsed = stop - start
    print("Parser took: " + str(int(elapsed)) + " seconds.")
