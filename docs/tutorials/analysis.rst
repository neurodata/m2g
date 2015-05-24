Analysis
********
 
First steps after processing your data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All data derivatives computed throughout the pipeline are made available. Analysis can be performed to assess the quality of intermediate steps of the pipeline, such as dice overlap for assessing image registration quality. This type of analysis can be useful when tuning parameters and ensuring that you are obtaining brain graphs that are meaningful for your data.

Basic Graph Statistics
~~~~~~~~~~~~~~~~~~~~~~
As was mentioned previously, we validate our pipelines using test-retest reliability. However, a perfect TRT score does not mean that the pipeline cannot further improve. Therefore, we needed to devise a better metric for assessing the quality and distributions of our graphs. Knowing the true subject/scan associations, we can leverage our graph difference as computed in our TRT calculation to form a distribution of inter- and intra-subject connectome differences. We are then able to compute the kernel density estimate of these distributions and compute the distance between them as well as the significance of our discrimination. In v1.1.0 of m2g, we measured a highly significant discrimination between same and different subject scans (< 1e-4) on the KKI2009 dataset.

Graph Analysis: Clustering
~~~~~~~~~~~~~~~~~~~~~~~~~~
A technique which has recently become popular when looking at graphs is vertex clustering. This can be done through many different algorithms such as sampling from stochastic block models (SBM), Louvain clustering, spectral clustering, to name a few. The small graphs produced by m2g are, in a statistical sense, a  graph which has been sampled from a stochastic block model with 70 regions. Looking at big graphs, we are able to cluster vertices and determine optimal scaling and partitioning of these graphs - i.e. find the optimal number of clusters for subsequent inference.

Graph Analysis: Inference
~~~~~~~~~~~~~~~~~~~~~~~~~
Inference tasks require datasets with covariates and phenotypic information along with their physical scans. From this information, one can build classifiers and decision rule classes that attempt to map from connectome properties to covariate information. These tasks are particularly interesting when thinking about the application of connectomics to medicine, as when paired with the right classifier a connectome may be able to serve as a powerful diagnostic tool.


Helping us
~~~~~~~~~~
As graph statistics are a young field, we are always looking for new ways to analyze the data we are producing, and learning valuable things from it. If you have interest or expertise in developing graph statistics and would like to help, we encourage you to get in touch with us and forging a collaboration.
