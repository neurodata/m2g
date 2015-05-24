Validation
**********

Since there is no ground truth data or gold standard available when estimating MR connectomes, we validate the effectiveness and quality of our pipeline using test-retest (TRT) reliability. A TRT compatible dataset is one which has had all subjects scanned multiple times. TRT is a metric which compares a derivative estimated from a particular subject on one scan to that of all other scans, and asserts that the most similar result must be from the same subject's other scan. The pipelines which we release have scored a TRT score of 42/42 on the KKI2009 dataset (figured below).

As it is difficult to assess improvements in development past a perfect TRT score, we are also using statistical measures, such as Hellinger Distance, to assess the quality of our pipeline. These methods will be looked at in the analysis section.

.. image:: ../images/m2g_trt.png

The code and data used to produce this plot are below.

.. raw:: html

	<script src="https://gist.github.com/gkiar/7f3b1b8fc5c7fe3e95c8.js"></script>
