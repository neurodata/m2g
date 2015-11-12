Validation
**********

Since there is no ground truth data or gold standard available when estimating MR connectomes, we validate the effectiveness and quality of our pipeline using test-retest (TRT) reliability. A TRT compatible dataset is one which has had all subjects scanned multiple times. Reliability leverages the assertion that your brain is more like your brain on another day than it is to anyone else's brain on any day. The value returned is a probability that this is true for a random subject in your dataset (i.e. if your dataset has perfect reliability then reliability is 1).

Computing Reliability on your Data
----------------------------------

In order to assess the reliability of your data derivates from m2g, you can use the following procedure. Note that this only applies for test retest datasets (i.e. each subject scanned at least twice).

* Run m2g on your data with atlas(es) of your choosing.
* Locate the base directory of your small graphs
* Run the reliability script in the m2g repo like as follows:

.. code-block:: none
  
  Rscript ${m2g}/analysis/compute_trt.R ${m2g} ${path_to_graphs} ${rois} ${format} ${scans} ${output_figure} ${output_stats}

* The returned text file will provide statistics about the outlier graphs in your set as well as the reliability of your data
* The returned figure is a heat map of the difference between pairs of braingraphs. Lower heat indicates higher similarity

Example outputs from this reliability script as well as the graphs used to generate them can be found `here <http://openconnecto.me/data/public/MR/m2g_v1_1_1/KKI2009/derivatives/sg/>`_. Note that more processed graphs can be obtained from our `graph services <ttp://mrbrain.cs.jhu.edu/graph-services/welcome/>`_, and those linked above are our nightly build.
