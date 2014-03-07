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
