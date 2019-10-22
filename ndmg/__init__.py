"""
ndmg
~~~~

an end-to-end connectome estimation pipeline
"""

# naming convention for __version__ : major.minor.bugs
__version__ = "0.3.0"


# to call `ndmg.graph`, etc
__all__ = ["scripts", "stats", "utils"]  # subpackages
__all__.extend(["graph", "preproc", "register", "track"])  # modules

# import everything listed in __all__
from . import *
