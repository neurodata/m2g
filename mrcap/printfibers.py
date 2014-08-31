
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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