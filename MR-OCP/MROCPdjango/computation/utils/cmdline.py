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

# cmdline.py
# Created by Disa Mhembere on 2014-06-10.
# Email: disa@jhu.edu

def parse_dict(in_list):
  """
  Command line dictionary parser
  @param in_list: the input list
  @return: The resulting dict
  """
  ret_dict = {}
  for item in in_list:
    sp = item.split(":")
    ret_dict[sp[0].strip()] = sp[1].strip()

  return ret_dict
