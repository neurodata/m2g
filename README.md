# ndmg

[![](https://img.shields.io/pypi/v/ndmg.svg)](https://pypi.python.org/pypi/ndmg)
![](https://travis-ci.org/neurodata/ndmg.svg?branch=master)
![](https://img.shields.io/badge/pep8-0E-green.svg?style=flat)
[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.60206.svg)](http://dx.doi.org/10.5281/zenodo.60206)
[![Code Climate](https://codeclimate.com/github/neurodata/ndmg/badges/gpa.svg)](https://codeclimate.com/github/neurodata/ndmg)
[![DockerHub](https://img.shields.io/docker/pulls/bids/ndmg.svg)](https://hub.docker.com/bids/ndmg)
[![OpenNeuro](http://bids.neuroimaging.io/openneuro_badge.svg)](https://openneuro.org)

NeuroData's MR Graphs package, **ndmg** (pronounced "***nutmeg***"), is the successor of the MRCAP, MIGRAINE, and m2g pipelines. **ndmg** combines dMRI and sMRI data from a single subject to estimate a high-level connectome reliably and scalably.

![](./docs/nutmeg.png)


### Installing ndmg
Installing **ndmg** is very simple! We have a few dependencies which must be installed, but once that's taken care of you are ready to dive in!

**ndmg** relies on: [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation), [DiPy](http://nipy.org/dipy/), [networkx](https://networkx.github.io/), and [nibabel](http://nipy.org/nibabel/), [numpy](http://www.numpy.org/) [scipy](http://www.scipy.org/), [scikit-learn](http://scikit-learn.org/stable/), [scikit-image](http://scikit-image.org/), [nilearn](http://nilearn.github.io/). You should install FSL through the instructions on their website. Then, you can install **ndmg** with one of the following commands:

#### Install from pip

    pip install ndmg

#### Install from Github

    git clone https://github.com/neurodata/ndmg
    cd ndmg
    python setup.py install

### Test your installation

We provide the ability to exercise our entire end to end pipeline in < 3 minutes on downsampled data.  The connectome produced may not have neurological significance, but this test should ensure that all of the pieces of the code and driver script still execute and is a great interface check.

    ndmg_demo-dwi

### Documentation

Check out our full [documentation](http://docs.neurodata.io/nddocs/mrgraphs/) on our website, or our [function reference](http://docs.neurodata.io/ndmg/) for more information about **ndmg**.

### Questions?
If you're having trouble, notice a bug, or want to contribute (such as a fix to the bug you may have just found) feel free to open a git issue or pull request. Enjoy!
