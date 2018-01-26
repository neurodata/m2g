# ndmg

[![](https://img.shields.io/pypi/v/ndmg.svg)](https://pypi.python.org/pypi/ndmg)
![](https://travis-ci.org/neurodata/ndmg.svg?branch=master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1161284.svg)](https://doi.org/10.5281/zenodo.1161284)
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

    pip install ndmg
 
The only known packages which require a specific version are `plotly` and `networkx`, due to backwards-compatability breaking changes.

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

    ndmg_demo_dwi

The connectome produced may not have neurological significance, as the data has been significantly downsampled, but this test should ensure that all of the pieces of the code and driver script execute properly. The expected output from the demo is shown below. Files will be downloaded and output data generated in `/tmp/small_demo/` and `/tmp/small_demo/outputs/`, respectively. If the graph properties summarized at the end of the execution below match those observed with your installation, the demo ran successfully.

    Getting test data...
    Archive:  /tmp/ndmg_demo.zip
       creating: ndmg_demo/
      inflating: ndmg_demo/MNI152NLin6_res-4x4x4_T1w.nii.gz
      inflating: ndmg_demo/MNI152NLin6_res-4x4x4_T1w_brain.nii.gz
       creating: ndmg_demo/sub-0025864/
       creating: ndmg_demo/sub-0025864/ses-1/
       creating: ndmg_demo/sub-0025864/ses-1/func/
      inflating: ndmg_demo/sub-0025864/ses-1/func/sub-0025864_ses-1_bold.nii.gz
       creating: ndmg_demo/sub-0025864/ses-1/dwi/
      inflating: ndmg_demo/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bvec
      inflating: ndmg_demo/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval
      inflating: ndmg_demo/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz
       creating: ndmg_demo/sub-0025864/ses-1/anat/
      inflating: ndmg_demo/sub-0025864/ses-1/anat/sub-0025864_ses-1_T1w.nii.gz
      inflating: ndmg_demo/desikan-res-4x4x4.nii.gz
      inflating: ndmg_demo/HarvardOxford_variant-thr25_res-4x4x4_lvmask.nii.gz
      inflating: ndmg_demo/MNI152NLin6_res-4x4x4_T1w_brainmask.nii.gz
    Creating output directory: /tmp/ndmg_demo/outputs
    Creating output temp directory: /tmp/ndmg_demo/outputs/tmp
    This pipeline will produce the following derivatives...
    DWI volume registered to atlas: /tmp/ndmg_demo/outputs/reg/dwi/sub-0025864_ses-1_dwi_aligned.nii.gz
    Diffusion tensors in atlas space: /tmp/ndmg_demo/outputs/tensors/sub-0025864_ses-1_dwi_tensors.npz
    Fiber streamlines in atlas space: /tmp/ndmg_demo/outputs/fibers/sub-0025864_ses-1_dwi_fibers.npz
    Graphs of streamlines downsampled to given labels: /tmp/ndmg_demo/outputs/graphs/desikan-res-4x4x4/sub-0025864_ses-1_dwi_desikan-res-4x4x4.gpickle
    Generating gradient table...
    B-values shape (15,)
             min 0.000000
             max 1000.000000
    B-vectors shape (15, 3)
             min -0.978756
             max 0.941755
    None
    Aligning volumes...
    Executing: eddy_correct /tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_dwi_t1.nii.gz /tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_dwi_t1_t2.nii.gz 0
    Executing: epi_reg --epi=/tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_dwi_t1_t2.nii.gz --t1=/tmp/ndmg_demo/sub-0025864/ses-1/anat/sub-0025864_ses-1_T1w.nii.gz --t1brain=/tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_T1w_ss.nii.gz --out=/tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_dwi_t1_ta.nii.gz
    Executing: flirt -in /tmp/ndmg_demo/sub-0025864/ses-1/anat/sub-0025864_ses-1_T1w.nii.gz -ref /tmp/ndmg_demo/MNI152NLin6_res-4x4x4_T1w.nii.gz -omat /tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_T1w_MNI152NLin6_res-4x4x4_T1w_xfm.mat -dof 12 -bins 256 -cost mutualinfo -searchrx -180 180 -searchry -180 180 -searchrz -180 180
    Executing: flirt -in /tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_dwi_t1_ta.nii.gz -ref /tmp/ndmg_demo/MNI152NLin6_res-4x4x4_T1w.nii.gz -out /tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_dwi_t1_ta2.nii.gz -init /tmp/ndmg_demo/outputs/tmp/sub-0025864_ses-1_T1w_MNI152NLin6_res-4x4x4_T1w_xfm.mat -interp trilinear -applyxfm
    Beginning tractography...
    Generating graph for desikan-res-4x4x4 parcellation...
    {'source': 'http://m2g.io', 'ecount': 0, 'vcount': 70, 'date': 'Fri Jan 19 00:15:32 2018', 'region': 'brain', 'sensor': 'dwi', 'name': "Generated by NeuroData's MRI Graphs (ndmg)"}
    # of Streamlines: 5772
    0
    288
    576
    864
    1152
    1440
    1728
    2016
    2304
    2592
    2880
    3168
    3456
    3744
    4032
    4320
    4608
    4896
    5184
    5472
    5760
    
     Graph Summary:
    Name: Generated by NeuroData's MRI Graphs (ndmg)
    Type: Graph
    Number of nodes: 70
    Number of edges: 887
    Average degree:  25.3429
    Execution took: 0:02:56.343901
    Complete!
    
    Parcellation: desikan-res-4x4x4
    Computing: NNZ
    Sample Mean: 887.00
    Computing: Degree Sequence
    Subject Means: 25.34
    Computing: Edge Weight Sequence
    Subject Means: 68.99
    Computing: Clustering Coefficient Sequence
    Subject Means: 0.75
    Computing: Max Local Statistic Sequence
    Subject Means: 24948.83
    Computing: Eigen Value Sequence
    Subject Maxes: 1.32
    Computing: Betweenness Centrality Sequence
    Subject Means: 0.01
    Computing: Mean Connectome
    This is the format of your plot grid:
    [ (1,1) x1,y1 ]  [ (1,2) x2,y2 ]  [ (1,3) x3,y3 ]  [ (1,4) x4,y4 ]
    [ (2,1) x5,y5 ]  [ (2,2) x6,y6 ]  [ (2,3) x7,y7 ]  [ (2,4) x8,y8 ]

    Path to qc fig: /tmp/ndmg_demo/outputs/qa/graphs/desikan-res-4x4x4/desikan-res-4x4x4_plot.html


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
