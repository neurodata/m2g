import warnings

warnings.simplefilter("ignore")
# from . import *

# so we don't have to type ndg.graph.graph(), etc., to get the classes
# from .graph import graph, biggraph
from .register.gen_reg import DmriReg as register
#from .register.gen_reg import epi_register as epi_register

# from .stats.qa_mri import qa_mri as qa_mri
# from .stats.group_func import group_func as group_func
from .track.gen_track import run_track as track

# from .stats import *
# from .preproc.preproc import preproc as preproc
from .scripts import ndmg_dwi_pipeline as ndmg_dwi_pipeline

VERSION = "0.2.0"
