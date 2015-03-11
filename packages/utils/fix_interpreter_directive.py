#!/usr/bin/env python

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

# fix_interpreter_directive.py
# Created by Disa Mhembere on 2014-05-16.
# Email: disa@jhu.edu
# A script to fix the shabang directive to a universally friendly one.

import argparse
import os

def add(files):
  global __license_header__

  for full_fn in files:
    print "Processing file: %s ..." % full_fn
    f = open(full_fn, "rb")
    lines = f.readlines()

    fix = False
    if lines[0] == "#!/usr/bin/python\n":
      lines[0] = "#!/usr/bin/env python\n"
      f.close()
      fix = True

    if fix:
      f = open(full_fn, "wb")
      f.write("".join(lines))

    f.close()

def hidden(path):
  breakdown = path.split("/")
  for item in breakdown:
    if item.startswith("."):
      return True
  return False

def main():
  parser = argparse.ArgumentParser(description="Add or Update license headers to code")
  parser.add_argument("-d", "--dirname", action="store", default=".", help="Directory where to start walk")
  parser.add_argument("-f", "--files", action="store", nargs="*", help="Files you want license added to")
  parser.add_argument("-e", "--file_exts", nargs="*", action="store", \
      default=[".py",""], \
      help="File extensions to add to the files altered")
  parser.add_argument("-i", "--ignore", nargs="*", action="store", \
      default=["README", "__init__.py", "TODO", __file__], \
      help="Files to ignore")

  result = parser.parse_args()

  if result.files:
    print "Fixing individual files ..."
    add(result.files)
    exit(1)
  
  else:
    print "Fixing a directory of files ..."
    files = []
    for root, dirnames, filenames in os.walk(os.path.abspath(result.dirname)):
      for filename in filenames:
        full_fn = os.path.join(root, filename)
        if os.path.isfile(full_fn) and not hidden(full_fn) \
            and not os.path.basename(full_fn) in result.ignore \
            and ( os.path.splitext(full_fn)[-1].lower().strip() in result.file_exts ):
          files.append(full_fn) 

    add(files)

if __name__ == "__main__":
  main()
