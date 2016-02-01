from distutils.core import setup
from setuptools import setup
import ndmg

VERSION = ndmg.version

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
    version=VERSION,
    description='Neuro Data MRI to Graphs Pipeline',
    author='Greg Kiar and Will Gray Roncal',
    author_email='gkiar@jhu.edu, wgr@jhu.edu',
    url='https://github.com/openconnectome/ndmg',
    download_url='https://github.com/openconnectome/ndmg/tarball/' + VERSION,
    keywords=[
        'connectome',
        'mri',
        'pipeline'
    ],
    classifiers=[],
    install_requires=[
        'python-igraph',
        'nibabel',
        'numpy',
        'scipy',
        'dipy'
    ]
)
