#!/usr/bin/env bash

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# m2g_full.sh
# Created by Greg Kiar on 2015-05-22.
# Email: gkiar@jhu.edu

#setup
  M2G_HOME=/mrimages/src/m2g
  #Working output directory
  DATA=/data
  #Structural image
  MPRAGE=/data/MPRAGE.nii
  #Diffusion image and scanner params
  DTI=/data/DTI.nii
  BVAL=/data/DTI.b
  BVEC=/data/DTI.bvec
  #Atlas image and labels
  MNI=${M2G_HOME}/data/Atlas/MNI152_T1_1mm.nii.gz
  MASK=${M2G_HOME}/data/Atlas/MNI152_T1_1mm_brain_mask.nii
  LABELS=${M2G_HOME}/data/Atlas/MNI152_T1_1mm_desikan_adjusted.nii

#PRE-PROCESSING + REGISTRATION
#Step 1: Parse B
#provide the b values and bvectors files for parsing. LONI will automatically string
#parse the output, but you'll need to manually inspect the output string to get the index 
#of the B0 volume and the value of B elsewhere.
BVEC_NEW=${DATA}/bvecs_new.grad
python2.7 ${M2G_HOME}/packages/dtipreproc/parse_b.py ${BVAL} ${BVEC} ${BVEC_NEW}
#in our dataset we saw the following:
B=700
B0=32

#Step 2: Extract B0
#using parsed b information, we read in the DTI volume and extract the B0 volume
B0_vol=${DATA}/B0volume.nii.gz
python2.7 ${M2G_HOME}/packages/dtipreproc/extract_b0.py ${DTI} ${B0} ${B0_vol}

#Step 3: Eddy correction
#a second use of the B0 index is the DTI alignment + eddy correction using fsl
DTI_aligned=${DATA}/DTI_aligned.nii.gz
eddy_correct ${DTI} ${DTI_aligned} ${B0}

#Step 4: Register B0 to MPRAGE || Register MPRAGE to MNI
#we compute the registration between the B0 volume and MPRAGE, and then into MNI space as well.
B0_in_MP=${DATA}/B0_in_MPRAGE.nii.gz
txm1=${DATA}/b0_mp.xfm
flirt -in ${B0} -ref ${MPRAGE} -out ${B0_in_MP} -omat ${txm1} -cost normmi -searchrx -180 180 -searchry -180 180 -searchrz -180 180

MP_in_MNI=${DATA}/MPRAGE_in_MNI.nii.gz
txm2=${DATA}/mp_mni.xfm
flirt -in ${MPRAGE} -ref ${MNI} -out ${MP_in_MNI} -omat ${txm2} -cost normmi -searchrx -180 180 -searchry -180 180 -searchrz -180 180

#Step 5: Apply registration to DTI
DTI_in_MP=${DATA}/DTI_in_MPRAGE.nii.gz
DTI_in_MNI=${DATA}/DTI_in_MNI.nii.gz
flirt -in ${DTI_aligned} -ref ${MPRAGE} -out ${DTI_in_MP} -init ${txm1} -applyxfm -paddingsize 0.0

flirt -in ${DTI_in_MP} -ref ${MNI} -out ${DTI_in_MNI} -init ${txm2} -applyxfm -paddingsize 0.0

#DTI PROCESSING
#Step 6: Tensor estimation
SCHEME=${DATA}/scheme.scheme
DTI_BFLOAT=${DATA}/DTI.Bfloat
TENSORS=${DATA}/DTI_tensors.Bdouble
python2.7 ${M2G_HOME}/packages/tractography/tensor_gen.py ${DTI_in_MNI} ${BVEC_NEW} ${B} ${MASK} ${SHEME} ${DTI_BFLOAT} ${TENSORS}

#Step 7: Fiber tractography
FIBERS=${DATA}/fibers.Bfloat
VTK=${DATA}/fibers.vtk
LOG=${DATA}/logfile.log
python2.7 ${M2G_HOME}/packages/tractography/fiber_gen.py ${TENSORS} ${MASK} 0.2 70 ${FIBERS} ${VTK} ${LOG} 

#Step 8: Fiber conversion
FIBERS_NEW=${DATA}/fibers.dat
python2.7 ${M2G_HOME}/packages/tractography/fiber_convert.py ${FIBERS} ${FIBERS_NEW}

#Step 9: Graph generation
GRAPH=${DATA}/graph.graphml
python2.7 ${M2G_HOME}/MR-OCP/mrcap/gengraph.py ${FIBERS_NEW} ${LABELS} ${GRAPH} --outformat graphml -a ${LABELS}

#Step 10: Graph conversion
GRAPH_NEW=${DATA}/graph.mat
python2.7 ${M2G_HOME}/packages/utils/graphml2mat.py ${GRAPH} ${GRAPH_NEW}
