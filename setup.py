from setuptools import setup, Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize


ext_modules = cythonize(Extension("ndmg.graph.zindex", # the extension name
                                  sources=["ndmg/graph/zindex.pyx"],
                                  include_dirs=['.'],
                                  language="c"))
VERSION="0.1.1"

setup(
    name='ndmg',
    ext_modules = ext_modules,
    packages=[
        'ndmg',
        'ndmg.preproc',
        'ndmg.register',
        'ndmg.track',
        'ndmg.graph',
        'ndmg.stats',
        'ndmg.utils',
        'ndmg.timeseries',
        'ndmg.nuis',
        'ndmg.scripts'
    ],
    version=VERSION,
    scripts = [
        'ndmg/scripts/ndmg_demo-dwi',
        'ndmg/scripts/ndmg_demo-qa',
        'ndmg/scripts/ndmg_demo-mrilab',
        'ndmg/scripts/ndmg_demo-func'
    ],
    entry_points = {
        'console_scripts': [
            'ndmg_dwi_pipeline=ndmg.scripts.ndmg_dwi_pipeline:main',
            'ndmg_func_pipeline=ndmg.scripts.ndmg_func_pipeline:main',
            'ndmg_bids=ndmg.scripts.ndmg_bids:main',
            'ndmg_cloud=ndmg.scripts.ndmg_cloud:main'
    ]
    },
    description='Neuro Data MRI to Graphs Pipeline',
    author='Greg Kiar, Will Gray Roncal and Eric Bridgeford',
    author_email='gkiar@jhu.edu, wgr@jhu.edu, ebridge2@jhu.edu',
    url='https://github.com/neurodata/ndmg',
    download_url='https://github.com/neurodata/ndmg/tarball/' + VERSION,
    keywords=[
        'connectome',
        'mri',
        'pipeline'
    ],
    classifiers=[],
    install_requires=[  # We didnt put versions for numpy, scipy, b/c travis-ci
        'networkx>=1.11',
        'nibabel>=2.0',
        'nilearn>=0.2',
        'sklearn>=0.0',
        'numpy',  # We use nump v1.10.4
        'scipy>=0.13.3',  # We use 0.17.0
        'dipy>=0.1',
        'boto3',
        'matplotlib==1.5.3',
        'plotly==1.12.1',
        'cython',
        'pybids'
    ]
)
