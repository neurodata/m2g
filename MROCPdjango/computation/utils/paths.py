"""
Code to load necessary paths
"""

import os, sys

COMPUTATION_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "/.." ))
sys.path += [COMPUTATION_BASE_PATH]

