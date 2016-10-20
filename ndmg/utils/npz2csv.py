#!/usr/local/bin/python2.7
# a script for converting from npz to csv format.
# written by eric bridgeford
# usage:
#    ./npz2csv.py npzpath csvpath
#
import numpy as np
from argparse import ArgumentParser

def npz2csv(npzname, csvname):
    data = np.load(npzname)['arr_0']
    np.savetxt(csvname, data)

def main():
    parser=ArgumentParser(description="")
    parser.add_argument("in_file", help="the npz file to convert to csv.")
    parser.add_argument("out_file", help="the csv file to be converted to.")
    result=parser.parse_args()
    npz2csv(result.in_file, result.out_file)

if __name__ == "__main__":
    main()

