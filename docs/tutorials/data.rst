Data Formats
************

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

Data derivatives for processed brains include the following data. They are organized by the following directory structure containing data as explained below:

.. code-block:: none

  ./{dataset}/
  ./{dataset}/derivatives/
  ./{dataset}/derivatives/reg/
  ./{dataset}/derivatives/fibers/
  ./{dataset}/derivatives/bg/
  ./{dataset}/derivatives/sg/

1. The ``reg`` directory contains image aligned DTI and MPRAGE volumes to the atlas space (default is MNI152). These are in the compressed nifti format.
2. The ``fibers`` directory contains fiber streamlines for the entire brain volume. These are in the MRIStudio format.
3. The ``bg`` directory contains big graphs (i.e. voxelwise graphs) in the graphml format.
4. The ``sg`` directory contains small graphs (i.e. parcellated by the input atlases) in the graphml format.

