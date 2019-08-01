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
    include_package_data = True,
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
    author_email="gkiar@jhu.edu, wgr@jhu.edu, ebridge2@jhu.edu",
    url="https://github.com/neurodata/ndmg",
    download_url="https://github.com/neurodata/ndmg/tarball/" + VERSION,  # I don't think we need this (this download url is a 404)
    keywords=["connectome", "mri", "pipeline"],
    classifiers=[],
    install_requires=[
        "networkx",
        "nibabel",
        "nilearn",
        "sklearn",
        "numpy",  # We use nump v1.10.4
        "scipy>=0.13.3",  # We use 0.17.0
        "dipy==0.16.0",
        "boto3",
        "matplotlib",
        "plotly==1.12.1",
        # "cython",
        "pybids==0.6.4",
        "configparser>=3.7.4",
        "pytest"
    ],
)
