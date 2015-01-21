
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
#
# Wrapper to generate a graph for every file in a directory
#
#

import argparse
import sys
import os
from gengraph import genGraph

#
# 
#
def main():

    parser = argparse.ArgumentParser(description='Process a directory containing MRI Studio files and generate a sparse graph in Matlab format.')
    parser.add_argument('inputdir', action="store")
    parser.add_argument('outputdir', action="store")
    parser.add_argument("--pattern", dest='pattern', action="store", default="", help="Process files matching this pattern only.  Matches any file with the specified substring.")

    result = parser.parse_args()

    try:
      # list of input files
      filelist = os.listdir ( result.inputdir )

      # create the output directory if it does not exist
      if not os.path.exists ( result.outputdir ):
        print "Making directory ", result.outputdir
        os.makedirs ( result.outputdir )
      else:
        if not os.path.isdir ( result.outputdir ):
          print "Output directory (0) is not a directory".format(result.outputdir)
          sys.exit (-1)

    except:
      print "Error handling directories"
      sys.exit (-1)

    for infile in filelist:
      if not result.pattern or ( infile.find ( result.pattern ) != -1):
        outfile = os.path.splitext(infile)[0]
        infp = os.path.normpath ( result.inputdir + '/' + infile )
        outfp = os.path.normpath ( result.outputdir + '/' + outfile + '.mat' )
        genGraph ( infp, outfp )
      else:
        pass

if __name__ == "__main__":
      main()