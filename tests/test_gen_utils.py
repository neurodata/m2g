import os

import pytest
import m2g
from m2g.utils.cloud_utils import s3_get_data
from pathlib import Path
from m2g.utils.gen_utils import create_datadescript, DirectorySweeper


@pytest.fixture
def input_dir_tree(tmp_path):
    data = {"002547": [1,2], "002548": [1], "002449": [1,2,3]}
    for sub, session in data.items():
        for ses in session:
            info = f"sub-{sub}/ses-{ses}"
            anat = os.path.join(tmp_path, info, "anat")
            dwi = os.path.join(tmp_path, info, "dwi")
            # make directories and files
            os.makedirs(anat)
            os.makedirs(dwi)
            tmpfilepath = os.path.join(anat, f"sub-{sub}_ses-{ses}_T1w.nii.gz")
            with open(tmpfilepath, "x") as f:
                f.write("placeholder text")
            tmpfilepath = os.path.join(dwi, f"sub-{sub}_ses-{ses}_dwi.bval")
            with open(tmpfilepath, "x") as f:
                f.write("placeholder text")
            tmpfilepath = os.path.join(dwi, f"sub-{sub}_ses-{ses}_dwi.bvec")
            with open(tmpfilepath, "x") as f:
                f.write("placeholder text")
            tmpfilepath = os.path.join(dwi, f"sub-{sub}_ses-{ses}_dwi.nii.gz")
            with open(tmpfilepath, "x") as f:
                f.write("placeholder text")

    # Empty Directory
    os.makedirs(os.path.join(tmp_path, "sub-002"))
    # Create non-BIDS files
    tmpfilepath = os.path.join(anat, f"dummy.txt")
    with open(tmpfilepath, "x") as f:
        f.write("placeholder text")
    tmpfilepath = os.path.join(dwi, f"sub-55.nii.gz")
    with open(tmpfilepath, "x") as f:
        f.write("placeholder text")

    # Create json file of input data
    create_datadescript(os.path.join(tmp_path))

    return tmp_path, data


def test_DirectorySweeper(input_dir_tree):
    input_dir, data = input_dir_tree
    for sub, session in data.items():
        for ses in session:
            sweeper = DirectorySweeper(str(input_dir), sub, ses)
            scans = sweeper.get_dir_info()
            # Check that all files exist
            for SubSesFiles in scans:
                _, _, files = SubSesFiles
                for type_, file_ in files.items():
                    assert os.path.exists(file_)

    # Check with no sub/ses specified
    sweeper = DirectorySweeper(str(input_dir))
    scans = sweeper.get_dir_info()
    for SubSesFiles in scans:
        _, _, files = SubSesFiles
        for type_, file_ in files.items():
            assert os.path.exists(file_)

    # Abnormal data
    bad_data = {"002547": 3, "002548": -1, "002449": 0.2}
    for sub, session in bad_data.items():
        with pytest.raises(ValueError):
            sweeper = DirectorySweeper(str(input_dir), sub, session)

    # Check that ancelary file isn't recorded
    assert (
        f"{str(input_dir_tree)}/sub-002448/ses-3/anat/dummy.txt"
        in sweeper.get_files("002449", "3").values()
    ) == False
    assert (
        f"{str(input_dir_tree)}/sub-002448/ses-3/dwi/sub-55.nii.gz"
        in sweeper.get_files("002449", "3").values()
    ) == False