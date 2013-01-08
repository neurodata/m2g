#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to all packages in the project to see each other
"""

#
# Code to load project paths
#

import os, sys

MR_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.." ))
MR_CMAPPER_PATH = os.path.join(MR_BASE_PATH, "cmapper" )
MR_MRCAP_PATH = os.path.join(MR_BASE_PATH, "mrcap" )

sys.path += [ MR_BASE_PATH, MR_CMAPPER_PATH, MR_MRCAP_PATH ]
