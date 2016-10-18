# fngs_multisubject.sh
#$1 = restfile
#$2 = anatfile
#$3 = /path/to/outdir

atlas='/path/to/atlas.nii.gz'
atlas_brain='/path/to/atlas_brain.nii.gz'
atlas_mask='/path/to/brain_mask.nii.gz'
label='/path/to/first/label.nii.gz /path/to/second/label.nii.gz'

exec 4<$1
exec 5<$2

while read -r rest <&4 && read -r anat<&5; do
    fngs_pipeline $rest $anat $atlas $atlas_brain $atlas_mask $3 $label --fmt graphml
done 4<$1 5<$2
