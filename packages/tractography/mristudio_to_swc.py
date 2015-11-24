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

# mristudio_to_swc.py
# Based on camino_to_mristudio.py (By Disa Mhembere)
# Created by Greg Kiar on 2015-06-29.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

from struct import pack

class SWC(object):
	"""
	This class represents an SWC format file.
	It writes out data in the format given a path which is
	defined by the SWC skeleton 
	"""

	def __init__(self, filename):
		"""
		@param filename: the output fn
		"""
		self.fhandle = open(filename, "wb")
		self.point = 0

	def write_header(self, head, orig):
		fhead = "# Original Fiber File: "+orig+"\n# FiberFileTag: " + head[0] + "\n# Number of Fibers: " + \
				str(head[1]) + "\n# Pipeline version: m2gv1.1.1\n"
		self.fhandle.write(fhead)

	def write_path(self, path):
		"""
		Write the path to disk
		@param path we want to write
		"""
		#import pdb; pdb.set_trace()
		for i in range(0, len(path)):
			self.point += 1
			node = str(self.point) + " 7 " + str(path[i][0]) + " " + str(path[i][1]) + " " + str(path[i][2]) + " 1 "
			if i == 0:
				node += "-1\n"
			else:
				node += str(self.point-1) + "\n"
			self.fhandle.write(node)

	def __del__ (self,):
		self.fhandle.close()
