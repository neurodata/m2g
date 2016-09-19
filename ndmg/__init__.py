from . import *

# so we don't have to type ndg.graph.graph(), etc., to get the classes
from .graph.graph import graph as graph
from .register.register import register as register
from .track.track import track as track
from .stats import *
from .stats.fmri_qc import fmri_qc as fmri_qc
# from .preproc.preproc import preproc as preproc
from .preproc.preproc import preproc as preproc
from .utils.utils import utils as utils
from .scripts import ndmg_pipeline as ndmg_pipeline
from .scripts import fngs_pipeline as fngs_pipeline

version = "0.0.31"
