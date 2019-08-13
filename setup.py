#!/usr/bin/env python

from setuptools import setup, Extension
from ndmg import VERSION


setup(
    name="ndmg",
    packages=[
        "ndmg",
        "ndmg.preproc",
        "ndmg.register",
        "ndmg.track",
        "ndmg.graph",
        "ndmg.stats",
        "ndmg.utils",
        "ndmg.timeseries",
        "ndmg.nuis",
        "ndmg.scripts",
    ],
    include_package_data=True,
    version=VERSION,
    entry_points={
        "console_scripts": [
            "ndmg_dwi_pipeline=ndmg.scripts.ndmg_dwi_pipeline:main",
            "ndmg_func_pipeline=ndmg.scripts.ndmg_func_pipeline:main",
            "ndmg_bids=ndmg.scripts.ndmg_bids:main",
            "ndmg_cloud=ndmg.scripts.ndmg_cloud:main",
        ]
    },
    description="Neuro Data MRI to Graphs Pipeline",
    author="Derek Pisner, Greg Kiar, Eric Bridgeford, Alex Loftus, and Will Gray Roncal",
    author_email="dpisner@utexas.edu, aloftus2@jhu.edu, gkiar@jhu.edu, wgr@jhu.edu, ebridge2@jhu.edu",
    url="https://github.com/neurodata/ndmg",
    download_url="https://github.com/neurodata/ndmg/tarball/"
    + VERSION,
    keywords=["connectome", "mri", "pipeline"],
    classifiers=["Programming Language :: Python :: 3.6"],
    install_requires=[
        "numpy",
        "nibabel",
        "dipy==0.16.0",
        "scipy",
        "python-dateutil",
        "pandas",
        "boto3",
        "awscli",
        "matplotlib",
        "nilearn",
        "sklearn",
        "vtk",
        "pyvtk",
        "fury",
        "requests",
        "plotly==1.12.9",
        "pybids==0.6.4",
        "setuptools>=40.0",
        "scikit-image",
        "networkx",
        "configparser>=3.7.4",
        "pytest",
    ],
)
