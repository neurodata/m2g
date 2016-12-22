#!/bin/bash

echo "Getting test data..."

loc="$PWD"
cd /tmp/
wget http://openconnecto.me/mrdata/share/demo_data/small_demo_func.zip
unzip /tmp/small_demo_func.zip
wget http://openconnecto.me/mrdata/share/demo_data/less_small_atlases.zip
unzip /tmp/less_small_atlases.zip

fngs_pipeline /tmp/small_func/sub-0025864_session-1_bold.nii.gz /tmp/small_func/sub-0025864_session-1_T1w.nii.gz /tmp/demo_atlases/atlas/MNI152_T1_2mm.nii.gz /tmp/demo_atlases/atlas/MNI152_T1_2mm_brain.nii.gz /tmp/demo_atlases/mask/MNI152_T1_2mm_brain_mask.nii.gz /tmp/small_func/outputs /tmp/demo_atlases/label/desikan_2mm.nii.gz -s interleaved

cd "$loc"
