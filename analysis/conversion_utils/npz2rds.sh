#!/bin/bash
# call from a directory where you want
# to have your npz files converted to rds files.
# written by eric bridgeford
#
# Usage:
#   ./npz2rds.sh /path/to/your/roi_timeseries
#

cd $(dirname "$0")

echo "$(pwd)"

while read -r npzline; do
    ./npz2csv.py $npzline ${npzline//.npz/.csv}
    ./csv2rds.R ${npzline//.npz/.csv} ${npzline//.npz/.rds}
done < <(find $1 -wholename "*roi_timeseries*.npz")

cd -
echo "$(pwd)"
