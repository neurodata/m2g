#!/usr/bin/env python

"""
FSL's eddy correct function which performs chromatic and geometric alignment of diffusion data.

The eddy correct tool in FSL both aligns DTI volumes to the B0 scan, as well as corrects for chromatic errors - namely, eddy currents created by the scanner. Eddy currents are inherent to MR imaging as the imposed magnetic field induces a perpendicular current. In the case of DTI, this is an issue as the direction of the magnetic field changes so eddy current direction also changes.

FSL's eddy correct documentation: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/EDDY

  Inputs
      - DTI volume: [X, Y, Z, D] DTI image stack from scanner.
      - B0 index: Location of the B0 scan in the DTI volume.
  Outputs
      - Corrected DTI: [X, Y, Z, D] DTI image stack which has been image aligned as well as eddy correction.
"""

import os

def main():
	pass

if __name__ == '__main__':
  main()
