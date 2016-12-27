#!/bin/bash

echo "Getting test data..."

loc="$PWD"
cd /tmp/
wget http://openconnecto.me/mrdata/share/demo_data/ndmg_demo.zip
unzip /tmp/ndmg_demo.zip
wget http://openconnecto.me/mrdata/share/atlases/fmri_atlases.zip
unzip /tmp/fmri_atlases.zip
res=3mm

fngs_pipeline /tmp/project_demo/sub-0025864_session-1_bold_small.nii.gz /tmp/project_demo/sub-0025864_session-1_T1w_small.nii.gz 1 /tmp/demo_atlases/atlas/MNI152_T1-${res}.nii.gz /tmp/demo_atlases/atlas/MNI152_T1-${res}_brain.nii.gz /tmp/demo_atlases/mask/MNI152_T1-${res}_brain_mask.nii.gz /tmp/demo_atlases/mask/HarvOx_lv_thr25-${res}.nii.gz /tmp/small_func/outputs /tmp/demo_atlases/label/desikan-${res}.nii.gz -s interleaved

cd "$loc"
