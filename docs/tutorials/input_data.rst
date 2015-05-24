Data Formats
*************

This is a draft input/output specfication for processing MR data.

Input Data
~~~~~~~~~~

Data to process must be organized in the following hierarchical format, by dataset or series:

**Dataset (series)**

- Subject

   - Scan

      - dti [Diffusion Tensor Imaging]
      - dsi [Diffusion Spectrum Imaging]
      - rest [Resting State functional scan]
      - anat [Anatomical Scan, e.g., MPRAGE]
      - params [b vals, gradients]


Output Data
~~~~~~~~~~~

Data derivatives for processed brains include the following data, tagged with its quarterly release.  For each data product, users select the product, the atlas (parcellation scheme) and data format:

1) graphs + atlas + format
2) derivative + atlas + format
3) subject covariates

Graphs range in size from O(10^1) to O(10^6), and intermediate products include graph invariants and processing artifacts (e.g., fibers, tensors).
