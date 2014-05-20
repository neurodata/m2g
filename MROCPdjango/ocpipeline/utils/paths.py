
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
# Created by Disa Mhembere
# Email: disa@jhu.edu
"""
Code to load project paths
"""

import os

MR_BASE_PATH = os.path.abspath("../../.." )
MR_DJANGO_PATH = os.path.join(MR_BASE_PATH, "MROCPdjango")
PATHS = [ MR_BASE_PATH, MR_DJANGO_PATH ]

def include():
  for path in PATHS:
    if path not in os.sys.path: os.sys.path.append(path)