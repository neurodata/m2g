#!/usr/bin/python

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
# propagate_license.py
# Created by Disa Mhembere on 2014-05-16.
# Email: disa@jhu.edu

__licence_header__ = """
{} Copyright 2014 Open Connectome Project (http://openconnecto.me)
{}
{} Licensed under the Apache License, Version 2.0 (the "License");
{} you may not use this file except in compliance with the License.
{} You may obtain a copy of the License at
{}
{}     http://www.apache.org/licenses/LICENSE-2.0
{}
{} Unless required by applicable law or agreed to in writing, software
{} distributed under the License is distributed on an "AS IS" BASIS,
{} WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
{} See the License for the specific language governing permissions and
{} limitations under the License.
{}
"""
COMM_COUNT = 14
comm = {".py":"#", ".pyx":"#", "": "#", ".html":"", ".sh":"#", ".R":"#", ".mat":"%", ".c":"//",
        ".c++":"//", ".java":"//", ".js":"//"}

import argparse
import os
import pdb

def add(dirname, file_exts):
  files_to_edit = []

  for root, dirnames, filenames in os.walk(os.path.abspath(dirname)):
    for filename in filenames:
      full_fn = os.path.join(root, filename)
      if os.path.isfile(full_fn) and not os.path.basename(full_fn).startswith(".") \
          and not os.path.basename(root).startswith(".") and ( os.path.splitext(full_fn)[-1].upper().strip() in file_exts ):
        print "Processing file: %s ..." % full_fn
        script = open(full_fn, "rb")
        lines = script.read().splitlines()
        script.close()
        # Exception for html
        if os.path.splitext(full_fn)[1].upper().strip() == ".HTML":
          __licence_header__ = "<!-- " + __licence_header__ + " -->"

        comment_style = comm[os.path.splitext(full_fn)[1]]
        if lines[0] == "#!/usr/bin/python":
          if lines[5].startswith("# Copyright"): # get rid of copyright year
            del lines[5], lines[1]

          lines.insert(1, __licence_header__.format(*([comment_style]*COMM_COUNT)))
        else:
          lines.insert(0, __licence_header__.format(*([comment_style]*COMM_COUNT)))

        script = open(full_fn, "wb")
        script.write("\n".join(lines))

  print "\n".join(files_to_edit)

def rm(dirname):
  pass

def main():
  parser = argparse.ArgumentParser(description="Add or Update license headers to code")
  parser.add_argument("-r", "--remove", action="store_true", help="Remove the license")
  parser.add_argument("-d", "--dirname", action="store", default=".", help="Directory where to start walk")
  parser.add_argument("-e", "--file_exts", nargs="*", action="store", \
      default=[".py", ".pyx", ".html", ".sh", ".R", ".mat", ""], \
      help="File extensions to add to the files altered")
  
  result = parser.parse_args()
  
  add(result.dirname, result.file_exts)

if __name__ == "__main__":
  main()
