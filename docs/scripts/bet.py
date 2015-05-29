#!/usr/bin/env python

"""
Extracts brain content from whole head image.

Using FSL's BET, we extract the brain of the MPRAGE scans from the entirity of the image. The reason for this extraction is to aid in registration, as well as provide a mask which allows algorithm to identify voxels of interest further down the pipeline.

FSL's BET documentation: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BET

**Positional Arguments**

		Input image: [nifti]
				- Structural T1 (MPRAGE) image from the MRI scanner.

**Returns**

		Output image: [nifti]
				- Structural T1 (MPRAGE) image in which all voxels not in the brain have been set to an intensity of zero.
		Output mask: [nifti]
				- Binary representation of the brain image

**Optional Arguments**

		Fractional intensity threshold: [float] (default = 0.4)
				- Value used to influence aggressiveness of segmentation
"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
