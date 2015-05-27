#!/usr/bin/env python

"""
Diffusion processing portion of the m2g workflow which analyzes diffusion information to estimate brain graphs.

In the diffusion processing workflow, the newly aligned DTI image is processed and then mapped to a set of defined labels. Specifically, tensors are estimated for each voxel, indicating the primary direction of water diffusion at that location in the brain.  It has been shown that this corresponds to the principal direction of travel for major white matter (axonal) connections in the brain.  From the tensors, fiber streamlines (or tracks) are created using deterministic algorithms. The fibers are then mapped to atlas regions defined by the inputted parcellation.

**Inputs**

		Registered DTI image: [nifti]
				- DTI image which has been denoised and aligned to the atlas space.
		DTI B vectors: [ASCII]
				- Orientation vectors of the scanner corresponding to the DTI image.
		DTI B values: [ASCII]
				- B value intensities of the scanner corresponding to the DTI image.
		Atlas brain mask: [nitfi]
				- Binary mask of the brain of the atlas image.
		Atlas labels: [nifti] (default = desikan)
				- Region labels/parcellations of the atlas image.

**Outputs**

		Brain Graph: [mat, graphml]
				- Graph of structural region connectivity of the subject.
"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
