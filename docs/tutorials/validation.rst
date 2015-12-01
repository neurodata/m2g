Validation
**********

Since there is no ground truth data or gold standard available when estimating MR connectomes, we validate the effectiveness and quality of our pipeline using test-retest (TRT) reliability. A TRT compatible dataset is one which has had all subjects scanned multiple times. Reliability leverages the assertion that your brain is more like your brain on another day than it is to anyone else's brain on any day. The value returned is a probability that this is true for a random subject in your dataset (i.e. if your dataset has perfect reliability then ths probability is 1).

The code which performs this evaluation lives `here <https://github.com/openconnectome/m2g/blob/gkiar-dev/analysis/compute_trt.R>`_.

Benchmark Evaluation
--------------------

We assess the performance and timing of our pipeline across several datasets ranging in number of subjects, diffusion directions, and quality of acquisition, in order to ensure that the pipeline produces useful derivatives for downstream inference tasks. The timing given below is that which it took to complete the small graphs, used here for analysis. Outlier graphs were removed from the population probability computation based on sufficiently low reliability scores (<0.5).

The following results are for version 1.1.1 of m2g.

========= ===== ======================= ============= ======== =============================
Dataset   Scans Fraction of scans used  Reliability   Atlas    Runtime per subject per core
========= ===== ======================= ============= ======== =============================
KKI2009   42    1.0                     1.00000       Desikan  6h
SWU4      454   0.863                   0.97605       Desikan  5h43min
========= ===== ======================= ============= ======== =============================

The KKI2009 dataset performed perfectly under this metric. This is high quality data with 34 diffusion directions.

The SWU4 dataset performed well after outlier removal. Though the dataset contains 470 subjects originally, only 454 scans exist with paired diffusion images. Of those, a subset contained sufficiently poor quality data that they (as well as the other session scan from the same subject) were eliminated from analysis. This data has 93 diffusion directions.

Based on these results, we conclude that m2g produces reliable and repeatable derivatives across a wide range of data quality and size.

The graphs analyzed above can be found in our `graph services <http://openconnecto.me/graph-services/>`_ or s3 bucket (contact `support <mailto:support@neurodata.io>`_ for access information).

Computing Reliability on your Data
----------------------------------

In order to assess the reliability of your data derivates from m2g, you can use the following procedure. Note that this only applies for test retest datasets (i.e. each subject scanned at least twice).

* Clone the m2g repository to your computer
* Locate the base directory of your small graphs
* Run the reliability script in the m2g repo like as follows:

.. code-block:: none
  
  Rscript ${m2g}/analysis/compute_trt.R ${m2g} ${path_to_graphs} ${rois} ${format} ${scans} ${output_figure} ${output_stats}

* The returned text file will provide statistics about the outlier graphs in your set as well as the reliability of your data
* The returned figure is a heat map of the difference between pairs of braingraphs. Lower heat indicates higher similarity

Example outputs from this reliability script as well as the graphs used to generate them can be found `here <http://openconnecto.me/data/public/MR/m2g_v1_1_1/KKI2009/derivatives/sg/>`_. Note that more processed graphs can be obtained from our `graph services <http://openconnecto.me/graph-services/welcome/>`_, and those linked above are our nightly build.
