#!/bin/bash

echo "Getting test data..."

loc="$PWD"
cd /tmp/
wget http://openconnecto.me/mrdata/share/demo_data/func_demo_full_res.zip
unzip /tmp/func_demo_full_res.zip
wget http://openconnecto.me/mrdata/share/demo_data/demo_atlases.zip
unzip /tmp/demo_atlases.zip

fngs_pipeline /tmp/func_demo_full_res/sub-0025864_session-1_bold.nii.gz /tmp/func_demo_full_res/sub-0025864_session-1_T1w.nii.gz 1 /tmp/demo_atlases/atlas/MNI152_T1-2mm.nii.gz /tmp/demo_atlases/atlas/MNI152_T1-2mm_brain.nii.gz /tmp/demo_atlases/mask/MNI152_T1-2mm_brain_mask.nii.gz /tmp/demo_atlases/mask/HarvOx_lv_thr25-2mm.nii.gz /tmp/small_func/outputs /tmp/demo_atlases/label/desikan-2mm.nii.gz -s interleaved


cd "$loc"
