#!/usr/bin/env python

"""
ndmg.preproc
~~~~~~~~~~~~

Contains functionality for normalizing b-vectors.
TODO : depracate or change name. Add other preprocessing functions created from ndmg_dwi_pipeline.
"""

# package imports
import numpy as np


def rescale_bvec(bvec, bvec_new):
    """Normalizes b-vectors to be of unit length for the non-zero b-values. If the b-value is 0, the vector is untouched

    Parameters
    ----------
    bvec : str
        Path to the original b-vectors file (bvec)
    bvec_new : str
        Path to the new (normalized) b-vectors file. Must have extension '.bvec'
    """

    bv1 = np.array(np.loadtxt(bvec))
    # Enforce proper dimensions
    bv1 = bv1.T if bv1.shape[0] == 3 else bv1

    # Normalize values not close to norm 1
    bv2 = [
        b / np.linalg.norm(b) if not np.isclose(np.linalg.norm(b), 0) else b
        for b in bv1
    ]

    try:
        assert "bvec" in bvec_new
        np.savetxt(bvec_new, bv2)
        pass
    except AssertionError:
        print(
            "Error: your new b-vector file must have extension .bvec to"
            + " be compatible with the the pipeline."
        )
        pass
    else:
        pass
    pass
