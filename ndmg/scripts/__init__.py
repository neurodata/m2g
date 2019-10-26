"""
ndmg.scripts
~~~~~~~~~~~~

Contains top-level, self-contained scripts.

ndmg_bids : top-level pipeline entrypoint
ndmg_dwi_pipeline : the pipeline itself
ndmg_cloud : for performing batch processing on AWS
"""

from . import ndmg_bids
from . import ndmg_cloud
from . import ndmg_dwi_pipeline
