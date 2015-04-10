MRImages to Graphs (M2G)
====================================

M2G is a pipeline which takes as input Diffusion Weighted MRI (DTI) data, and produced structural connectomes (brain graphs) as a result.

The pipeline makes use of FSL brain extraction, ANTs image registration, Camino tensor estimation and tractography, and igraph graph generation.

This project also contains several tools to play with fiber data in: [MRI Studio format](http://www.mristudio.org/).

Running M2G from EC2
--------------------

(This service has yet to be fully implemented)
In order to make use of our services and begin uploading and processing your data, you must do the following:

* Go to our webpage and request an account
* Upload your data to an Amazon S3 Bucket
* When your account is granted, you will receive an email with account and server information
* Download and Install the [LONI client](http://pipeline.loni.usc.edu)
* Connect to the server in LONI using your credentials
* Select the workflow you wish to run from the server library
* (tbd) link the S3 bucket to our server
* In your workflow, set the input and output requirements paths to locations in your bucket
* Validate workflow to ensure paths exist and files are found
* Begin running workflow, you will receive an email containing a link to your QC page once the job has completed

MROCP
=====
This section of the repository consists of processing and publishing tools which allow for interfacing between the tools presented here and the OCP web services.

MRCAP
-----
The `mrcap` subdirectory contains the source code that generates graphs from dMRI streamlines.  It produces two varieties of output:

- **smallgraphs**: these use brain atlas regions of interest (70) to make 70x70 adjacency matrix graphs.
- **biggraphs**: these create connectivities among greymatter voxels and make .

All graphs are [igraph](igraph.sourceforge.net) graphs that are written to disk in [graphml](graphml.graphdrawing.org) format.

CMAPPER
-------
The `cmapper` directory contains simple tools to manipulate connectome mapper outputs.

MROCPdjango
-----------
The `MROCPdjango` directory contains code developed for hosted Web-services for building brain-graphs and computing invariants. More info on Web-services can be obtained directly from [openconnecto.me/graph-services](http://openconnecto.me/graph-services).


More info?
----------
See our project [web page ](http://openconnectome.github.io/m2g/).
This is part of the bigger **Johns Hopkins University** Open Connectome project found [here](http://www.ocp.me/).
