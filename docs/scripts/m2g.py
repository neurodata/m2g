#!/usr/bin/env python

"""
Complete m2g workflow which estimates brain graphs from multimodal MRI images.

Starting with raw image data of both structural and diffusion varieties, diffusion scanner parameters, and an atlas which the subject is being compared to, the m2g workflow estimates a brain graph for a subject. In order to submit inputs to the pipeline, files names must be entered in the form of list files (enumerated ASCII text files with one item per line) and submitted to the workflow. The standard MNI152 atlas is currently distributed with our tools, though a user may use a pediatric atlas or another which is most suitable for their data.

  Inputs
      - MPRAGE image (.nii): Raw 3D structural image of the subject.
      - DTI image (.nii): Raw 4D diffusion image (3D + diffusion directions) of the subject.
      - DTI B vectors (ASCII text): Orientation vectors of the scanner corresponding to the DTI image.
      - DTI B values (ASCII text): B value intensities of the scanner corresponding to the DTI image.
      - Atlas image (.nii) (default=MNI152): Structural template T1 image to which the atlas labels are aligned.
      - Atlas brain mask (.nii): Binary mask of the brain of the atlas image.
      - Atlas labels (.nii) (default=desikan): Region labels/parcellations of the atlas image.
  Outputs
      - Brain Graph (.mat, .graphml): Graph of structural region connectivity of the subject.

"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
