Magnetic Resonance (MR-) Connectome
====================================

This project contains several tools to play with fiber data in
[MRI Studio format](http://www.mristudio.org/).

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
See our project [web page ](http://openconnectome.github.com/MR-connectome/).
This is part of the bigger **Johns Hopkins University** Open Connectome project found [here](http://www.openconnectomeproject.org/).
