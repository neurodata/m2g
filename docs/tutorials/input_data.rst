Data Formats
*************

This is a draft input/output specfication for discussion.  Open questions:

- Do we want to organize by subject or derivative?  Subject is clearer, but almost all analysis prefers derivative ordering (e.g., an entire folder of small graphs)
- How much data conversion should we do for the end user automatically (graphML vs. MAT vs. edgelist...)
- How can we track different versions?

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

Data derivatives for processed brains include the following data:

**Graphs**

- Small Graphs
- Big Graphs
- Graphs based on other parcellations

**Derivative and Intemediate Products**

- Big Invariants
- Big LCC
- Big LCC Graphs
- Small Graphs GraphML
- Small Invariants
- Small LCC

- Embeddings
- Fibers
- Subject Covariates
- MNI Data
- Tensors
