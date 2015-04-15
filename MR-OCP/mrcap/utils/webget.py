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

# webget.py
# Created by Disa Mhembere on 2015-04-15.
# Email: disa@jhu.edu
# Get a file from the web. Only works for Linux and Mac

from subprocess import call

def wget(out_fn, url):
 ret = call(["wget", "-O", out_fn, url])
 if ret != 0:
   ret = call(["curl", "-o", out_fn, url])

 assert ret == 0, "Non-zero return exit from command 'wget' and 'curl'. \
     Please add 'wget' or 'curl' package to your system"

if __name__ == "__main__":
  main()
