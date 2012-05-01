
#
# Simple script to show how to read the contents of a MRI Studio files.
#
#

import argparse
import sys

from fiber import FiberReader

def main():
    parser = argparse.ArgumentParser(description='Demo script to read the contents of MRI Studio files.')
    parser.add_argument('--count', action="store", type=int, default=-1)
    parser.add_argument('file', action="store")

    result = parser.parse_args()
    reader = FiberReader(result.file)

    print(reader)

    count = 0

    for fiber in reader:
        print(fiber)
        count += 1
        if result.count > 0 and count >= result.count:
            break

    del reader

    return

if __name__ == "__main__":
      main()
