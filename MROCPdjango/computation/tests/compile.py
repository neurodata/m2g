#!/usr/bin/python

# compile_all.py
# Created by Disa Mhembere on 2014-02-26.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

#!/usr/bin/python

# intergrtest
# Created by Disa Mhembere on 2013-06-03.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.
"""
Test to insure all scripts in the current module do not throw
'compile time' errors
"""
from glob import glob
from subprocess import call
import sys

def test():
  """
  The testing function traverses all modules for compilation
  errrors
  """
  todo = None

  files = list(set(glob("*.py"))-set([__file__]))


  for fn in files :
    if fn == __file__:
      print "Skipping '%s' ..." % __file__

    print "compiling %s ..." % fn
    v = call(["python", fn, "-h"])
    if v == 0:
      print "=====> %s compile SUCCESS!\n" % fn
    else:
      print "**[ERROR]: %s compile FAILED!***\n\n" % fn
      print "Continue to run test on remaining scripts ? yes or no ?"

      todo = sys.stdin.readline().strip()
      if todo == "n" or todo == "no":
        print "[ERROR message]: Remaining tests not run. Please correct error & rerun the testscript."
        sys.exit(-1)

  if not todo:
    print "\n**Congratulations! Your modules all compiled successfully!**\n\n"
  else:
    print "\n**[ERROR message]: Tests completed with errors. Please check which scripts failed and rerun the test.**\n\n"

if __name__ == '__main__':
  test()
