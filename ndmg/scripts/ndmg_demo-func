#!/bin/bash

echo "Getting test data..."

loc="$PWD"
cd /tmp/
wget http://openconnecto.me/mrdata/share/demo_data/ndmg_demo.zip
unzip /tmp/ndmg_demo.zip
wget http://openconnecto.me/mrdata/share/atlases/fmri_atlases.zip
unzip /tmp/fmri_atlases.zip
res=4mm

fngs_pipeline /tmp/ndmg_demo/sub-0025864_session-1_bold_small.nii.gz /tmp/ndmg_demo/sub-0025864_session-1_T1w_small.nii.gz 1 /tmp/atlases/atlas/MNI152_T1-${res}.nii.gz /tmp/atlases/atlas/MNI152_T1-${res}_brain.nii.gz /tmp/atlases/mask/MNI152_T1-${res}_brain_mask.nii.gz /tmp/atlases/mask/HarvOx_lv_thr25-${res}.nii.gz /tmp/ndmg_test/outputs /tmp/atlases/label/desikan-${res}.nii.gz -s interleaved

#ndmg_pipeline /tmp/ndmg_demo/sub-0025864_session-1_dwi.nii.gz /tmp/ndmg_demo/sub-0025864_session-1_dwi.bval /tmp/ndmg_demo/sub-0025864_session-1_dwi.bvec /tmp/ndmg_demo/sub-0025864_session-1_T1w_small.nii.gz /tmp/atlases/atlas/MNI152_T1_${res}.nii.gz /tmp/atlases/mask/MNI152_T1_${res}_brain_mask.nii.gz /tmp/ndmg_test/outputs /tmp/atlases/label/desikan-${res}.nii.gz


cd "$loc"
