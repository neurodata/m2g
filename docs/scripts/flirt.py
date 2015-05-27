#!/usr/bin/env python

"""
FSL's linear registration tool for aligning multimodal MRI images.

The linear registration tool in FSL, FLIRT, allows us to both compute and apply registration transforms between image spaces. This tool uses affine registration, and is implemented here to transform DTI data into structural MPRAGE space, as well as the MPRAGE image into standard MNI space.

FSL's FLIRT documentation: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT

**Inputs**

		Input image: [nifti]
				- The 3D image which is to be transformed.
		Reference image: [nifti]
				- The 3D image which will be the target of the transformation.
		Search range: [2x float] (default = -180 180)
				- Orientation angles to search when aligning images.
		Transform matrix: [xfm] -optional
				- If previously computed, the matrix which maps from the original image to the reference image.

**Outputs**

		Registered image: [nifti]
				- The input image aligned to the reference image space.
		Transform matrix: [xfm] -optional
				- The matrix which maps from the original image to the reference image. This option and the input transformation matrix are mutually exclusive.
"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
