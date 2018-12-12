from distutils.core import setup
from setuptools import setup

VERSION = "0.1.0"

setup(
    name='ndmg',
    packages=[
        'ndmg',
        'ndmg.preproc',
        'ndmg.register',
        'ndmg.track',
        'ndmg.graph',
        'ndmg.stats',
        'ndmg.utils',
        'ndmg.scripts'
    ],
    scripts = [
        'ndmg/scripts/ndmg_demo_dwi',
    ],
    entry_points = {
        'console_scripts': [
            'ndmg_dwi_pipeline=ndmg.scripts.ndmg_dwi_pipeline:main',
            'ndmg_bids=ndmg.scripts.ndmg_bids:main',
            'ndmg_cloud=ndmg.scripts.ndmg_cloud:main'
    ]
    },
    version=VERSION,
    description='Neuro Data MRI to Graphs Pipeline',
    author='Greg Kiar, Eric Bridgeford, Will Gray Roncal',
    author_email='gkiar@jhu.edu, ebridge2@jhu.edu, wgr@jhu.edu',
    url='https://github.com/neurodata/ndmg',
    download_url='https://github.com/neurodata/ndmg/tarball/' + VERSION,
    keywords=[
        'connectome',
        'mri',
        'pipeline'
    ],
    classifiers=[],
    install_requires=[  # We didnt put versions for numpy, scipy, b/c travis-ci
        'networkx==1.9',
        'nibabel>=2.0',
        'nilearn>=0.2',
        'sklearn>=0.0',
        'numpy',  # We use nump v1.10.4
        'scipy>=0.14',  # We use 0.17.0
        'dipy>=0.1',
        'boto3',
        'matplotlib==1.5.1',
        'plotly==1.12',
        'seaborn==0.9.0',
    ],
    include_package_data=True,
)
