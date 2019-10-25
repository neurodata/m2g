"""
ndmg
~~~~

an end-to-end connectome estimation pipeline
"""

# naming convention for __version__ : major.minor.bugs
__version__ = "0.3.0"


# to call `ndmg.graph`, etc
__all__ = ["graph", "preproc", "register", "track"]  # modules
__all__.extend(["scripts", "stats", "utils"])  # subpackages

# import everything listed in __all__
from . import *
