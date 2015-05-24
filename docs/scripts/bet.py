#!/usr/bin/env python

"""
Extracts brain content from whole head image.

Using FSL's BET, we extract the brain of the MPRAGE scans from the entirity of the image. The reason for this extraction is to aid in registration, as well as provide a mask which allows algorithm to identify voxels of interest further down the pipeline.

FSL's BET documentation: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BET

  Inputs
      - MPRAGE Image: X x Y x Z structural T1 image from the MRI scanner.
      - Fractional Intensity Threshold (0.4): Value used to influence aggressiveness of segmentation
  Outputs
      - Brain image: X x Y x Z structural T1 image in which all voxels not in the brain have been set to an intensity of zero.
      - Brain mask: Binary representation of the Brain image
"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
