""" First pytest file for ndmg. Basic assertions that don't mean anything for now just to make sure pytest + travis works."""

import os

import pytest
import ndmg
from ndmg.utils.cloud_utils import s3_get_data
from pathlib import Path
from ndmg.utils.gen_utils import create_datadescript, DirectorySweeper
import tempfile

KEYWORDS = ["sub", "ses"]


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

    #Empty Directory
    os.makedirs(os.path.join(tmp_path,'sub-002'))
    # Create non-BIDS files
    tmpfilepath = os.path.join(anat, f"dummy.txt")
    with open(tmpfilepath, "x") as f:
        f.write("placeholder text")
    tmpfilepath = os.path.join(dwi, f"sub-55.nii.gz")
    with open(tmpfilepath, "x") as f:
        f.write("placeholder text")

    # Create json file of input data
    create_datadescript(os.path.join(tmp_path))

    return tmp_path


def test_DirectorySweeper(input_dir_tree):
    data = {'002547':2, '002548':1, '002449':3}
    for sub, session in data.items():
        for ses in range(1,session+1):
            sweeper=DirectorySweeper(str(input_dir_tree),sub,ses)
            scans = sweeper.get_dir_info()
            # Check that all files exist
            for SubSesFiles in scans:
                _, _, files = SubSesFiles
                for type_, file_ in files.items():
                    assert os.path.exists(file_)
    
    #Check with no sub/ses specified
    sweeper=DirectorySweeper(str(input_dir_tree))
    scans = sweeper.get_dir_info()
    for SubSesFiles in scans:
        _, _, files = SubSesFiles
        for type_, file_ in files.items():
            assert os.path.exists(file_)
    
    #Abnormal data
    data = {'002547':3, '002548':-1, '002449':0.2}
    for sub, session in data.items():
        sweeper=DirectorySweeper(str(input_dir_tree),sub,session)
        scans=sweeper.get_dir_info()
        pairs = sweeper.get_pairs(sub,session)
        assert pairs==[]
    
    # Check that ancelary file isn't recorded
    assert (f'{str(input_dir_tree)}/sub-002448/ses-3/anat/dummy.txt' in sweeper.get_files('002449','3').values())==False
    assert (f'{str(input_dir_tree)}/sub-002448/ses-3/dwi/sub-55.nii.gz' in sweeper.get_files('002449','3').values())==False

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
