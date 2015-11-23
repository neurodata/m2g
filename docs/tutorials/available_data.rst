Public Data
===========

Many publicly available datasets exist which contain diffusion and strutural MRI images in the form of nifti or dicom files, and contain diffusion protocol parameters. These images can be viewed in any standard nifti viewer, generally, such as ITKSnap, mricron, FSLview, Paraview, and others.

We process all publicly available data we can find, and put the graphs in our `graph services <http://http://openconnecto.me/graph-services/>`_ engine. This service is under expansion and will contain other derivatives as well in the near future.

Data Formats and Access
-----------------------

Below are the data items that you both need to input and will receive out of m2g, a description of the expected datatype of these items, as well as a suggested tool used to interact with each of them. All of these tools exist on Mac, Windows, and Linux, at the time of this writing.

================ =============== ============== =======================================
Data             Raw/Derivative  Datatype       Recommended tool for interaction
================ =============== ============== =======================================
DTI Scan         Raw             .nii, .nii.gz  mricron
b-values         Raw             ASCII text     Sublime Text
b-vectors        Raw             ASCII text     Sublime Text
MPRAGE Scan      Raw             .nii, .nii.gz  mricron
Aligned DTI      Derivative       .nii, .nii.gz  mricron
Aligned MPRAGE   Derivative       .nii, .nii.gz  mricron
Fibers           Derivative      .dat           MRIStudio
Big graphs       Derivative      .graphml       igraph (library for Python, R, C)
Small graphs     Derivative      .graphml       igraph (libarry for Python, R, C)
================ =============== ============== =======================================
