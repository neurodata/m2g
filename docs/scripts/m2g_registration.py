#!/usr/bin/env python

"""
Registration portion of the m2g workflow which aligns diffusion data to the atlas space.

In the registration workflow, diffusion and structural images are preprocessed (e.g, skull-stripped and denoised), and then registered.  Specifically, DTI volumes undergo eddy current correction and are registered to the B0 reference scan. The B0 scan is then registered to the structural MPRAGE image, and the MPRAGE image is registered to the atlas (e.g., MNI152) space.  Finally, these transforms are combined to create a DTI volume in atlas space so that scans and subjects can be easily compared.  

  Inputs
      - MPRAGE image (.nii): Raw 3D structural image of the subject.
      - DTI image (.nii): Raw 4D diffusion image (3D + diffusion directions) of the subject.
      - DTI B values (ASCII text): B value intensities of the scanner corresponding to the DTI image.
      - Atlas image (.nii) (default=MNI152): Structural template T1 image to which the atlas labels are aligned.
  Outputs
      - Registered DTI image (.nii): DTI image which has been denoised and aligned to the atlas space.

"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
