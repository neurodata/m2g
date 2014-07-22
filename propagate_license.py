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

__license_header__ = """
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
comm = {".py":"#", ".pyx":"#", "": "#", ".html":"", ".sh":"#", ".r":"#", ".m":"%", ".c":"//",
        ".c++":"//", ".java":"//", ".js":"//"}

import argparse
import os

def add(files):
  global __license_header__

  for full_fn in files:
    license_header = __license_header__

    print "Processing file: %s ..." % full_fn
    script = open(full_fn, "rb")
    lines = script.read().splitlines()
    script.close()
    # Exception for html

    comment_style = comm[os.path.splitext(full_fn)[1].lower()]
    if lines[0] == "#!/usr/bin/python":
      if lines[5].startswith("# Copyright"): # get rid of copyright year
        del lines[5], lines[1]

      lines.insert(1, license_header.format(*([comment_style]*COMM_COUNT)))
    else:
      #license_header += "{} Created by Disa Mhembere\n{} Email: disa@jhu.edu".format(*([comment_style]*2))
      if os.path.splitext(full_fn)[1].lower().strip() == ".html":
        license_header = "<!-- " + license_header + " -->"

      lines.insert(0, license_header.format(*([comment_style]*COMM_COUNT)))
    script = open(full_fn, "wb")
    script.write("\n".join(lines))

def hidden(path):
  breakdown = path.split("/")
  for item in breakdown:
    if item.startswith("."):
      return True
  return False

def rm(dirname):
  pass

def main():
  parser = argparse.ArgumentParser(description="Add or Update license headers to code")
  parser.add_argument("-r", "--remove", action="store_true", help="Remove the license")
  parser.add_argument("-d", "--dirname", action="store", default=".", help="Directory where to start walk")
  parser.add_argument("-f", "--files", action="store", nargs="*", help="Files you want license added to")
  parser.add_argument("-e", "--file_exts", nargs="*", action="store", \
      default=[".py", ".pyx", ".html", ".sh", ".R", ".m", ""], \
      help="File extensions to add to the files altered")
  parser.add_argument("-i", "--ignore", nargs="*", action="store", \
      default=["README", "__init__.py", "TODO", __file__], \
      help="Files to ignore")
  
  result = parser.parse_args()
  
  if result.files:
    print "Licensing individual files ..."
    add(result.files)
    exit(1)
  
  else:
    print "Licensing a directory of files ..."
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
