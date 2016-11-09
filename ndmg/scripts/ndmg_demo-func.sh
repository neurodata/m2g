#!/bin/bash

echo "Getting test data..."

loc="$PWD"
cd /tmp/
wget http://openconnecto.me/mrdata/share/demo_data/small_demo_func.zip
unzip /tmp/small_demo_func.zip
wget http://openconnecto.me/mrdata/share/demo_data/small_atlases.zip
unzip /tmp/small_atlases.zip

fngs_pipeline /tmp/small_func/sub-0025864_session-1_bold.nii.gz /tmp/small_func/sub-0025864_session-1_T1w.nii.gz /tmp/small_atlases/MNI152_T1_1mm_s4.nii.gz /tmp/small_atlases/MNI152_T1_1mm_brain_s4.nii.gz /tmp/small_atlases/MNI152_T1_1mm_brain_mask_s4.nii.gz /tmp/small_func/outputs /tmp/small_atlases/desikan_s4.nii.gz -s interleaved

cd "$loc"
