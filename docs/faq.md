## Parcellations/Atlases

**Q: What are the Desikan labels?**

**A:** The labels for the Desikan atlas can be found [here](http://openconnecto.me/data/public/MR/atlases/parcellations/raw/desikan.txt).

**Q: What are the spatial coordinates for the Desikan labels?**

**A:** The centroids for Desikan atlas regions can be found [here](https://github.com/neurodata/ndgrutedb/raw/master/MR-OCP/mrcap/utils/centroids.mat).

## DTI Pipeline


## fMRI Pipeline

**Q: The fMRI output directory has several folders -- what do each of them contain?**

**A:** The folders are as follows:
- `connectome`: Functional connectomes (i.e. correlation of time-series) at multiple scales.
- `motion_fmri`: Motion corrected fMRI images.
- `nuis_fmri`: Nuisance corrected fMRI images.
- `preproc_fmri`: Fully pre-processed fMRI images.
- `qc`: Quality control figures for processed fMRI images.
- `reg_fmri`: Aligned fMRI images.
- `reg_struct`: Aligned T1/MPRAGE images.
- `roi_timeseries`: Region-of-interest parcellated time-series signals from the aligned fMRI image.
- `tmp`: Temporary output storage created during execution
- `voxel_timeseries`: Time-series signals for each voxel in the preprocessed and aligned fMRI image. 
