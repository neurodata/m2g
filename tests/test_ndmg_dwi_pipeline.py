""" First pytest file for ndmg. Basic assertions that don't mean anything for now just to make sure pytest + travis works."""

import os

import pytest
import ndmg
from ndmg.utils.cloud_utils import s3_get_data
from pathlib import Path
from ndmg.utils.gen_utils import create_datadescript, DirectorySweeper
import tempfile

KEYWORDS = ["sub", "ses"]



#/input/sub-{sub}/ses-{ses}/
#                           anat/sub-{sub}_ses-{ses}_T1w.nii.gz
#                           dwi/sub-{sub}_ses-{ses}_dwi.(bval,bvec,nii.gz)
@pytest.fixture
def input_dir_tree(tmp_path):
    data = {'002547':2, '002548':1, '002449':3}
    for sub, session in data.items():
        for ses in range(1,session+1):
            info = f'sub-{sub}/ses-{ses}'
            anat = os.path.join(tmp_path, info, 'anat')
            dwi = os.path.join(tmp_path, info, 'dwi')
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

    # Create json file of input data
    create_datadescript(os.path.join(tmp_path))

    return tmp_path


@pytest.fixture
def dirsweep(input_dir_tree):
    sweeper = DirectorySweeper(str(input_dir_tree))
    return sweeper

def test_DirectorySweeper(dirsweep):
    sweeper=dirsweep
    scans = sweeper.get_dir_info()
    assert os.path.exists(scans[0].files['bvals'])

def is_graph(filename, atlas="", suffix=""):
    """
    Check if `filename` is a ndmg graph file.

    Parameters
    ----------
    filename : str or Path
        location of the file.

    Returns
    -------
    bool
        True if the file has the ndmg naming convention, else False.
    """

    if atlas:
        atlas = atlas.lower()
        KEYWORDS.append(atlas)

    if suffix:
        if not suffix.startswith("."):
            suffix = "." + suffix

    correct_suffix = Path(filename).suffix == suffix
    correct_filename = all(i in str(filename) for i in KEYWORDS)
    return correct_suffix and correct_filename


def filter_graph_files(file_list, **kwargs):
    """
    Generator.
    Check if each file in `file_list` is a ndmg edgelist,
    yield it if it is.

    Parameters
    ----------
    file_list : iterator
        iterator of inputs to the `is_graph` function.
    """
    for filename in file_list:
        if is_graph(filename, **kwargs):
            yield (filename)


def get_files(output_directory, suffix="csv", atlas="desikan"):
    output = []
    for dirname, _, files in os.walk(output_directory):
        file_ends = list(filter_graph_files(files, suffix=suffix, atlas=atlas))
        graphnames = [Path(dirname) / Path(graphname) for graphname in file_ends]
        if all(graphname.exists for graphname in graphnames):
            output.extend(graphnames)
    return output


@pytest.fixture
def edgelists():
    """ Only works when the output directory is "/output", which it is in the travis build. """
    return get_files("/output")


def test_for_outputs(edgelists):
    """
    Test that, within the output directory on this subject, there is a graph.
    """
    assert edgelists


def test_for_content(edgelists):
    for filename in edgelists:
        with filename.open() as f:
            lines = f.readlines()
            assert lines
