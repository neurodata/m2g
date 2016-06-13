![](./docs/nutmeg.png)

# ndmg

[![](https://img.shields.io/pypi/v/ndmg.svg)](https://pypi.python.org/pypi/ndmg)
![](https://travis-ci.org/neurodata/ndmg.svg?branch=master)
![](https://img.shields.io/badge/pep8-0E-green.svg?style=flat)
[![Neurodata.io](https://img.shields.io/badge/Visit-neurodata.io-ff69b4.svg)](http://neurodata.io/)

NeuroData's MR Graphs package, **ndmg** (pronounced "***nutmeg***"), is the successor of the MRCAP, MIGRAINE, and m2g pipelines. **ndmg** combines dMRI and sMRI data from a single subject to estimate a high-level connectome reliably and scalably.

### Installing ndmg
Installing **ndmg** is very simple! We have a few dependencies which must be installed, but once that's taken care of you are ready to dive in!

**ndmg** relies on: [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation), [DiPy](http://nipy.org/dipy/), [networkx](https://networkx.github.io/), and [nibabel](http://nipy.org/nibabel/), as well as [numpy](http://www.numpy.org/) and [scipy](http://www.scipy.org/). You should install FSL through the instructions on their website. Then, you can install **ndmg** with one of the following commands:

#### Install from pip

    pip install ndmg

#### Install from Github

    git clone https://github.com/neurodata/ndmg
    cd ndmg
    python setup.py install

### Test your installation

We provide the ability to exercise our entire end to end pipeline in < 3 minutes on downsampled data.  The connectome produced may not have neurological significance, but this test should ensure that all of the pieces of the code and driver script still execute and is a great interface check.

    python ndmg/scripts/ndmg_pipeline.py tests/data/KKI2009_113_1_DTI_s4.nii tests/data/KKI2009_113_1_DTI_s4.bval tests/data/KKI2009_113_1_DTI_s4.bvec tests/data/KKI2009_113_1_MPRAGE_s4.nii tests/data/MNI152_T1_1mm_s4.nii.gz tests/data/MNI152_T1_1mm_brain_mask_s4.nii.gz tests/data/outputs tests/data/desikan_s4.nii.gz

### Documentation

Check out our full [documentation](http://docs.neurodata.io/nddocs/mrgraphs/) on our website, or our [function reference](http://docs.neurodata.io/ndmg/) for more information about **ndmg**.

### Questions?
If you're having trouble, notice a bug, or want to contribute (such as a fix to the bug you may have just found) feel free to open a git issue or pull request. Enjoy!
