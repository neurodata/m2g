# ndmg

[![](https://img.shields.io/pypi/v/ndmg.svg)](https://pypi.python.org/pypi/ndmg)
![](https://travis-ci.org/neurodata/ndmg.svg?branch=master)
[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.60206.svg)](http://dx.doi.org/10.5281/zenodo.60206)
[![Code Climate](https://codeclimate.com/github/neurodata/ndmg/badges/gpa.svg)](https://codeclimate.com/github/neurodata/ndmg)
[![DockerHub](https://img.shields.io/docker/pulls/bids/ndmg.svg)](https://hub.docker.com/r/bids/ndmg)
[![OpenNeuro](http://bids.neuroimaging.io/openneuro_badge.svg)](https://openneuro.org)

![](./docs/nutmeg.png)

NeuroData's MR Graphs package, **ndmg** (pronounced "***nutmeg***"), is a turn-key pipeline which combines structrual, diffusion, and functional\* MRI data to estimate multi-resolution connectomes reliably and scalably.

## Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Docker](#docker)
- [Demo](#demo)
- [Usage](#usage)
- [Example Datasets](#example-datasets)
- [Documentation](#documentation)
- [License](#license)
- [Manuscript Reproduction](#manuscript-reproduction)
- [Issues](#issues)

## Overview

The **ndmg** pipeline has been developed as a one-click solution for human connectome estimation by providing robust and reliable estimates of connectivity across a wide range of datasets. The pipelines are explained and derivatives analyzed in our pre-print, available on [BiorXiv](https://www.biorxiv.org/content/early/2017/09/16/188706).

## System Requirements

The **ndmg** pipeline:
 - was developed and tested primarily on Mac OSX, Ubuntu (12, 14, 16), and CentOS (5, 6);
 - was developed in Python 2.7;
 - is wrapped in a [Docker container](https://hub.docker.com/r/bids/ndmg/);
 - has install instructions via a [Dockerfile](https://github.com/BIDS-Apps/ndmg/blob/master/Dockerfile#L6);
 - requires no non-standard hardware to run;
 - has key features built upon FSL, Dipy, Nibabel, Nilearn, Networkx, Numpy, Scipy, Scikit-Learn, and others;
 - takes approximately 1-core, 8-GB of RAM, and 1 hour to run for most datasets.

While **ndmg** is quite robust to Python package versions (with only few exceptions, mentioned in the [installation guide](#installation-guide)), an *example* of possible versions (taken from the **ndmg** Docker Image with version `v0.0.50`) is shown below. Note: this list excludes many libraries which are standard with a Python distribution, and a complete list with all packages and versions can be produced by running `pip freeze` within the Docker container mentioned above.

```
awscli==1.11.128 , boto3==1.4.5 , botocore==1.5.91 , colorama==0.3.7 , dipy==0.12.0 , matplotlib==1.5.1 ,
networkx==1.11 , nibabel==2.1.0 , nilearn==0.3.1 , numpy==1.8.2 , Pillow==2.3.0 , plotly==1.12.9 ,
s3transfer==0.1.10 , scikit-image==0.13.0 , scikit-learn==0.18.2 , scipy==0.13.3 .
```

## Installation Guide

**ndmg** relies on [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation), [Dipy](http://nipy.org/dipy/), [networkx](https://networkx.github.io/), and [nibabel](http://nipy.org/nibabel/), [numpy](http://www.numpy.org/) [scipy](http://www.scipy.org/), [scikit-learn](http://scikit-learn.org/stable/), [scikit-image](http://scikit-image.org/), [nilearn](http://nilearn.github.io/). You should install FSL through the instructions on their website, then follow install other Python dependencies with the following:

    pip install numpy scipy dipy networkx nibabel nilearn scikit-learn scikit-image awscli boto3 colorama matplotlib plotly==1.12.9

As shown above, the only known package which requires a specific version is `plotly`, due to a backwards-compatability breaking change in the interface at version `1.13`.

Finally, you can install **ndmg** either from `pip` or Github as shown below. Installation shouldn't take more than a few minutes, but depends on your internet connection.

### Install from pip

    pip install ndmg

### Install from Github

    git clone https://github.com/neurodata/ndmg
    cd ndmg
    python setup.py install
    
Currently, functional processing lives only in a development branch, so if you wish to have functional processing as well you can intervene between the 2nd and 3rd lines above, and install the package as follows:

    git clone https://github.com/neurodata/ndmg
    cd ndmg
    git checkout m3r-release
    python setup.py install

## Docker

**ndmg** is available through Dockerhub, and can be run directly with the following container (and any additional options you may require for Docker, such as volume mounting):

    docker run -ti --entrypoint /bin/bash bids/ndmg

## Demo

You can run our entire end-to-end pipeline in approximately 3 minutes on downsampled data with the following command:

    ndmg_demo-dwi

The connectome produced may not have neurological significance, as the data has been significantly downsampled, but this test should ensure that all of the pieces of the code and driver script execute properly. The expected output from the demo is:

    Getting test data...
    Archive:  /tmp/small_demo.zip
      inflating: small_demo/desikan.nii.gz
      inflating: small_demo/KKI2009_113_1_DTI_s4.bval
      inflating: small_demo/KKI2009_113_1_DTI_s4.bvec
      inflating: small_demo/KKI2009_113_1_DTI_s4.nii
      inflating: small_demo/KKI2009_113_1_MPRAGE_s4.nii
      inflating: small_demo/MNI152_T1_1mm_brain_mask_s4.nii.gz
      inflating: small_demo/MNI152_T1_1mm_s4.nii.gz
    Creating output directory: /tmp/small_demo/outputs
    Creating output temp directory: /tmp/small_demo/outputs/tmp
    This pipeline will produce the following derivatives...
    DTI volume registered to atlas: /tmp/small_demo/outputs/reg_dti/KKI2009_113_1_DTI_s4_aligned.nii.gz
    Diffusion tensors in atlas space: /tmp/small_demo/outputs/tensors/KKI2009_113_1_DTI_s4_tensors.npz
    Fiber streamlines in atlas space: /tmp/small_demo/outputs/fibers/KKI2009_113_1_DTI_s4_fibers.npz
    Graphs of streamlines downsampled to given labels: /tmp/small_demo/outputs/graphs/desikan/KKI2009_113_1_DTI_s4_desikan.gpickle
    Generating gradient table...
    B-values shape (17,)
         min 0.000000
         max 700.000000
    B-vectors shape (17, 3)
         min -0.991788
         max 1.000000
    None
    Aligning volumes...
    Executing: eddy_correct /tmp/small_demo/outputs/tmp/KKI2009_113_1_DTI_s4_t1.nii.gz /tmp/small_demo/outputs/tmp/KKI2009_113_1_DTI_s4_t1_t2.nii.gz 16
    Executing: bet /tmp/small_demo/KKI2009_113_1_MPRAGE_s4.nii /tmp/small_demo/outputs/tmp/KKI2009_113_1_MPRAGE_s4_ss.nii.gz -B
    Executing: epi_reg --epi=/tmp/small_demo/outputs/tmp/KKI2009_113_1_DTI_s4_t1_t2.nii.gz --t1=/tmp/small_demo/KKI2009_113_1_MPRAGE_s4.nii --t1brain=/tmp/small_demo/outputs/tmp/KKI2009_113_1_MPRAGE_s4_ss.nii.gz --out=/tmp/small_demo/outputs/tmp/KKI2009_113_1_DTI_s4_t1_ta.nii.gz
    Executing: flirt -in /tmp/small_demo/KKI2009_113_1_MPRAGE_s4.nii -ref /tmp/small_demo/MNI152_T1_1mm_s4.nii.gz -omat /tmp/small_demo/outputs/tmp/KKI2009_113_1_MPRAGE_s4_MNI152_T1_1mm_s4_xfm.mat -cost mutualinfo -bins 256 -dof 12 -searchrx -180 180 -searchry -180 180 -searchrz -180 180
    Executing: flirt -in /tmp/small_demo/outputs/tmp/KKI2009_113_1_DTI_s4_t1_ta.nii.gz -ref /tmp/small_demo/MNI152_T1_1mm_s4.nii.gz -out /tmp/small_demo/outputs/tmp/KKI2009_113_1_DTI_s4_t1_ta2.nii.gz -init /tmp/small_demo/outputs/tmp/KKI2009_113_1_MPRAGE_s4_MNI152_T1_1mm_s4_xfm.mat -interp trilinear -applyxfm
    Beginning tractography...
    Generating graph for desikan parcellation...
    {'ecount': 0, 'vcount': 70, 'region': 'brain', 'source': 'http://m2g.io', 'version': '0.0.50', 'date': 'Sun Oct 29 17:49:05 2017', 'sensor': 'Diffusion MRI', 'name': "Generated by NeuroData's MRI Graphs (ndmg)"}
    # of Streamlines: 8906
    0
    445
    890
    1335
    1780
    2225
    2670
    3115
    3560
    4005
    4450
    4895
    5340
    5785
    6230
    6675
    7120
    7565
    8010
    8455
    8900
    
     Graph Summary:
    Name: Generated by NeuroData's MRI Graphs (ndmg)
    Type: Graph
    Number of nodes: 70
    Number of edges: 773
    Average degree:  22.0857
    Execution took: 0:02:36.341239
    Complete!

## Usage

The **ndmg** pipeline can be used to generate connectomes as a command-line utitlity on [BIDS datasets](http://bids.neuroimaging.io) with the following:

    ndmg_bids /input/bids/dataset /output/directory participant

Note that more options are available which can be helpful if running on the Amazon cloud, which can be found and documented by running `ndmg_bids -h`. If you do not have a BIDS organized dataset, you an use a slightly more complicated interface which is made available and is documented with `ndmg_pipeline -h`.

If running with the Docker container shown above, the `entrypoint` is already set to `ndmg_bids`, so the pipeline can be run directly from the host-system command line as follows:

    docker run -ti -v /path/to/local/data:/data bids/ndmg /data/ /data/outputs participant

## Example Datasets

Derivatives have been produced on a variety of datasets, all of which are made available on [our website](http://m2g.io). Each of these datsets is available for access and download from their respective sources. Alternatively, example datasets on the [BIDS website](http://bids.neuroimaging.io) which contain diffusion data can be used and have been tested; `ds114`, for example.

## Documentation

Check out some [resources](http://m2g.io) on our website, or our [function reference](http://docs.neurodata.io/ndmg/) for more information about **ndmg**.

## License

This project is covered under the [Apache 2.0 License](https://github.com/neurodata/ndmg/blob/m3r-release/LICENSE.txt).

## Manuscript Reproduction

The figures produced in our manuscript linked in the [Overview](#overview) are all generated from code contained within Jupyter notebooks and made available at our [paper's Github repository](https://github.com/neurodata/ndmg-paper).

## Issues

If you're having trouble, notice a bug, or want to contribute (such as a fix to the bug you may have just found) feel free to open a git issue or pull request. Enjoy!
