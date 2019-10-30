#!/usr/bin/env python
"""
setup.py
~~~~~~~~

on package install:
- generates metadata
- installs json files for use in ndmg_cloud
- installs `ndmg` script keywords to the command line
- ensures python version
- installs ndmg dependencies

Use `pip install .` to install the package.
Use `pip install -e .` to install the package in developer mode.
See our README for more details on package installation : https://github.com/neurodata/ndmg/blob/staging/README.md
"""

from setuptools import setup, find_packages
from ndmg import __version__

# initial setup
kwargs = {}

# add metadata
kwargs.update(
    dict(
        name="ndmg",
        version=__version__,
        description="Neuro Data MRI to Graphs Pipeline",
        author="Derek Pisner, Alex Loftus, Greg Kiar, Eric Bridgeford, and Will Gray Roncal",
        author_email="dpisner@utexas.edu, aloftus2@jhu.edu, gkiar@jhu.edu, wgr@jhu.edu, ebridge2@jhu.edu",
        url="https://github.com/neurodata/ndmg",
        download_url="https://github.com/neurodata/ndmg/tarball/" + __version__,
        keywords=["connectome", "mri", "pipeline"],
        classifiers=["Programming Language :: Python :: 3.6"],
    )
)

# add utility info
kwargs.update(
    dict(
        packages=find_packages(),
        package_data={"templates": ["*.json"]},
        include_package_data=False,  # only include the ndmg_cloud template jsons
        entry_points={
            "console_scripts": [
                "ndmg=ndmg.scripts.ndmg_bids:main",
                "ndmg_dwi_pipeline=ndmg.scripts.ndmg_dwi_pipeline:main",
                "ndmg_cloud=ndmg.scripts.ndmg_cloud:main",
                "ndmg_bids=ndmg.scripts.ndmg_bids:main",  # for backwards compatibility
            ]
        },
        python_requires=">=3.6",
    )
)

# add requirements
kwargs.update(
    dict(
        install_requires=[
            "nibabel",
            "numpy",
            "dipy>=1.0.0",
            "scipy",
            "boto3",
            "awscli",
            "matplotlib",
            "nilearn",
            "vtk",
            "pyvtk",
            "fury",
            "requests",
            "plotly",
            "pybids>=0.9.0",
            "scikit-image",
            "networkx>=2.4",
            "configparser>=3.7.4",
            "pytest",
        ]
    )
)

# run setup
setup(**kwargs)
