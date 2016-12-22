#!/bin/bash

echo "Getting test data..."

loc="$PWD"
cd /tmp/
wget http://openconnecto.me/mrdata/share/demo_data/project_demo.zip
unzip /tmp/project_demo.zip
wget http://openconnecto.me/mrdata/share/demo_data/less_small_atlases.zip
unzip /tmp/less_small_atlases.zip

fngs_pipeline /tmp/project_demo/sub-0025864_session-1_bold.nii.gz /tmp/project_demo/sub-0025864_session-1_T1w.nii.gz 1 /tmp/demo_atlases/atlas/MNI152_T1-4mm.nii.gz /tmp/demo_atlases/atlas/MNI152_T1-4mm_brain.nii.gz /tmp/demo_atlases/mask/MNI152_T1-4mm_brain_mask.nii.gz /tmp/demo_atlases/mask/HarvOx_lv_thr25-4mm.nii.gz /tmp/small_func/outputs /tmp/demo_atlases/label/desikan-4mm.nii.gz -s interleaved

cd "$loc"
