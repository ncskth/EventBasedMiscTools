#!/usr/bin/python

import sys, getopt
import scipy.io as sio
import numpy
from numpy import genfromtxt
import time
import csv
import pdb
import matplotlib.pyplot as plt

def plotHistogram(data, figName):

        # An "interface" to matplotlib.axes.Axes.hist() method
        n, bins, patches = plt.hist(x=data, bins=40, range = (0, 800000), color='#0504aa', alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Events/100ms')
        plt.ylabel('Frequency')
        plt.title('Event Occurrence Distribution')
        maxfreq = n.max()
        plt.ylim(ymax=20)

        plt.savefig(figName)
        # plt.show()

def extract(argv):

    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"i:",["ifile="])
    except getopt.GetoptError:
        print('analysis.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg


    start = time.time()
    my_data = genfromtxt(inputfile, delimiter=',')
    stop = time.time()
    print("Loading file took: " + str(int(stop-start)) + " seconds.")
    t = my_data[:,0]
    x = my_data[:,1]
    y = my_data[:,2]
    p = my_data[:,3]


    print("Number of events: " + str(t.size) + " in " + str((t[-1]-t[0])/1000000) + " seconds")
    print(str(t.size/((t[-1]-t[0])/100000)) + " every 100 ms")

    prior = t[0]
    delta = 100*1000 #100ms


    start = time.time()

    c = 0
    a = []
    for i in range(t.size):
        if t[i] <= prior + delta:
            c += 1
        else:
            # pdb.set_trace()
            a.append(c)
            c = 0
            prior = t[i]

    stop = time.time()
    print("Analysis took: " + str(int(stop-start)) + " seconds.")
    figName = inputfile.replace('.csv','.png')
    plotHistogram(a,figName)


if __name__ == "__main__":

    d = extract(sys.argv[1:])
