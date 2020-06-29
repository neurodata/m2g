""" First pytest file for m2g. Basic assertions that don't mean anything for now just to make sure pytest + travis works."""

import os

import pytest
import m2g
from m2g.utils.cloud_utils import s3_get_data
from pathlib import Path
from m2g.utils.gen_utils import create_datadescript, DirectorySweeper

KEYWORDS = ["sub", "ses"]


def is_graph(filename, atlas="", suffix=""):
    """
    Check if `filename` is a m2g graph file.

    Parameters
    ----------
    filename : str or Path
        location of the file.

    Returns
    -------
    bool
        True if the file has the m2g naming convention, else False.
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
    Check if each file in `file_list` is a m2g edgelist,
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
