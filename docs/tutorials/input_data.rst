Data Formats
*************

This is a draft input/output specfication for processing MR data.

Input Data
~~~~~~~~~~

Data to process must be organized in the following hierarchical format, by dataset. Subject names must also follow the convention highlighted here. For datasets which only have 1 scan collected per subject, the scan id of 1 should be used.

**Dataset**

.. code-block:: none

  ./{dataset}/
  ./{dataset}/raw/
  ./{dataset}/raw/{subject_id}/
  ./{dataset}/raw/{subject_id}/{subject_id}_{scan_id}/
  ./{dataset}/raw/{subject_id}/{subject_id}_{scan_id}/{dataset}_{subject_id}_{scan_id}_{modality}.{extension}
  ...

For instance, this directory structure and naming convention can be seen for the first subject of the KKI2009 dataset as follows:

.. code-block:: none

  ./KKI2009/
  ./KKI2009/raw/
  ./KKI2009/raw/113/
  ./KKI2009/raw/113/113_1/
  ./KKI2009/raw/113/113_1/KKI2009_113_1_DTI.b
  ./KKI2009/raw/113/113_1/KKI2009_113_1_DTI.nii
  ./KKI2009/raw/113/113_1/KKI2009_113_1_MPRAGE.nii
  ./KKI2009/raw/113/113_1/KKI2009_113_1_DTI.grad
  ./KKI2009/raw/113/113_2/KKI2009_113_2_DTI.b
  ./KKI2009/raw/113/113_2/KKI2009_113_2_DTI.nii
  ./KKI2009/raw/113/113_2/KKI2009_113_2_MPRAGE.nii
  ./KKI2009/raw/113/113_2/KKI2009_113_2_DTI.grad
  ...

Output Data
~~~~~~~~~~~

Data derivatives for processed brains include the following data, tagged with its quarterly release.  For each data product, users select the product, the atlas (parcellation scheme) and data format:

1) graphs + atlas + format
2) derivative + atlas + format
3) subject covariates

Graphs range in size from O(10^1) to O(10^6), and intermediate products include graph invariants and processing artifacts (e.g., fibers, tensors).
