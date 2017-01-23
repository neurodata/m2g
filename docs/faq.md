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
