from . import *

# so we don't have to type ndg.graph.graph(), etc., to get the classes
from .graph.graph import graph as graph
from .qc.qc import qc as qc
from .register.register import register as register
from .track.track import track as track
from .stats import *
# from .preproc.preproc import preproc as preproc
from .preproc.preproc import preproc as preproc
from .utils.utils import utils as utils
from .scripts import ndmg_pipeline as ndmg_pipeline
from .scripts import fmri_pipeline as fmri_pipeline

version = "0.0.31"
