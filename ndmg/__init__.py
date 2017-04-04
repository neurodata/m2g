from . import *

# so we don't have to type ndg.graph.graph(), etc., to get the classes
from .graph.graph import graph as graph
from .utils import utils
from .register.register import register as register
from .register.register import func_register as func_register
from .stats.qa_func import qa_func as qa_func
from .stats.group_func import group_func as group_func
from .track.track import track as track
from .stats import *
# from .preproc.preproc import preproc as preproc
from .timeseries import timeseries as timeseries
from .scripts import ndmg_dwi_pipeline as ndmg_dwi_pipeline
from .scripts import ndmg_func_pipeline as ndmg_func_pipeline

version = "0.0.49"
