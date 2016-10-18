#!/home/eric/anaconda2/bin/python
#
# Usage:
# ./fngs_multisubject.py /path/to/rest/files/by/line /path/to/anat/files/by/line /path/to/output/dir


import sys
import argparse
from ndmg.scripts.fngs_pipeline import fngs_pipeline
from multiprocessing import Process


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('restfile', help="the input file whose lines are " +\
                        "the resting state fMRI images.")
    parser.add_argument('anatfile', help="the input file whose lines are" +\
                        " the anatomical images.")
    parser.add_argument('outdir', help="the path to the output directory" +\
                        " where outputs will be placed.")
    atlas = "/home/eric/design_team/dependencies/atlas/MNI152_T1_2mm.nii.gz"
    atlas_brain = "/home/eric/design_team/dependencies/" +\
        "atlas/MNI152_T1_2mm_brain.nii.gz"
    mask = "/home/eric/design_team/dependencies/mask/" +\
        "MNI152_T1_2mm_brain_mask.nii.gz"
    labels = ["/home/eric/design_team/dependencies/label/desikan_2mm.nii.gz",
              "/home/eric/design_team/dependencies/label/Talairach_2mm.nii.gz"]

    results = parser.parse_args()
    with open(results.restfile) as restfile:
        with open(results.anatfile) as anatfile:
            restpaths = [l[:-1] for l in restfile.readlines()]
            anatpaths = [l[:-1] for l in anatfile.readlines()]
            for (rest, anat) in zip(restpaths, anatpaths):
                try:
                    p = Process(target=fmri_pipeline, args=(rest, anat,
                                atlas, atlas_brain, mask, labels,
                                results.outdir),
                                kwargs={'clean':False, 'fmt':'graphml'})
                    p.start()
                    p.join()
                except Exception as e:
                    print(e)

if __name__ == "__main__":
    main()
