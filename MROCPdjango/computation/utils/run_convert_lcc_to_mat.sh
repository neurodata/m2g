#!/bin/bash

directories="/data/public/MR/MIGRAINE/KKI-42_MIGRAINE_v1_0_2013-09-25/big_graphs
/data/public/MR/MIGRAINE/MRN-111_MIGRAINE_v1_0_2013-10-18/big_graphs
/data/public/MR/MIGRAINE/NKI-24_MIGRAINE_v1_0_2013-09-11/big_graphs
/data/public/MR/MIGRAINE/NKI-ENH_MIGRAINE_v1_0_2013-10-27/big_graphs
"
for f in $directories
do
  #echo $f
  python convert_lcc_to_mat.py $f
done

