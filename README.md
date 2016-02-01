# Welcome to ndmg!
DTI Connectome Estimation from structural MR Images (**now on pip!!!**) 

This page describes how brain graphs are generated in our service from Diffusion Weighted MRI (dMRI), and structural MRI (sMRI) images of human brains, as well as a template atlas (MNI152, for instance). The MRImages to Graphs (m2g) pipeline is the successor of MRCAP, MIGRAINE, and m2g. ndmg combines dMRI and sMRI data from a single subject to estimate a high-level connectome. The connectomes returned describe regions of connectivity within the brain at multiple levels of resolution in the form of a graph - where a node ranges from a single voxel scale ~1 mm^3 to large cortical regions ~20 cm^3.

Our pipeline has now been rewritten using PEP-8 compliant python and can now be installed using pip!

We are currently processing brain scans, and the resulting graphs are made available to the community on an ongoing basis.

This tutorial will lead you through installing the **ndmg** (pronounced "***nutmeg***") package, and lead you all along the way to using one of the pre-made pipelines for connectome estimation from diffusion and structural MRI.

### Installing ndmg
Installing **ndmg** is very simple! We have a few dependencies which must be installed, but once that's taken care of you are ready to dive in!

**ndmg** relies on: [FSL](), [DiPy](), [igraph](), and [nibabel]() primarily, as well as more standard libraries such as [numpy]() and [scipy](). You should install FSL through the instructions on their website, and then dipy and igraph using the command `pip install dipy python-igraph nibabel`. Then, you can install **ndmg** with:

    pip install ndmg

### Readying your data
Once **ndmg** is installed, the next thing you need to do is track down your data. If you don't have data readily available, you can [borrow some of ours](). The data you'll need are the following:

- 1 MPRAGE image
- 1 DTI image
- 1 DTI b-values file
- 1 DTI b-vectors file

In the interest of comparing results, **ndmg** performs operations in a predefined *atlas* space. In order for this to work you'll need, who would've guessed, an atlas! We recommend the MNI152 atlas and the Desikan parcellation, and you can [download them here]() (if you've downloaded the demo data you're good to go - we thought ahead).

**ndmg** expects the DTI and MPRAGE images in a nifti format, and the b-values and b-vectors files to be ASCII text files with the extensions `.bval` and `.bvec`, respectively. If you are unsure if you data is formatted correctly, please feel free to [download our demo data]() and check for yourself!

### Using ndmg
Now that your data is all set and ready to use, let's put **ndmg** to work! Let's give our end-to-end pipeline a shot. We're going to assume that you are using our demo data and you've stored it in your home directory. Open a new terminal and type the following:

~~~
python ndmg_pipeline.py ~/data/KKI2009_113_1_DTI.nii ~/data/KKI2009_113_1_DTI.bval ~/data/KKI2009_113_1_DTI.bvec ~/data/KKI2009_113_1_MPRAGE.nii ~/atlas/MNI152_T1_1mm.nii.gz ~/atlas/MNI152_T1_1mm_brain_mask.nii.gz ~/data/outputs ~/atlas/desikan.nii.gz
~~~

To break that down a bit, let's look at the arguments specifically:

~~~
python ndmg_pipeline.py dti bval bvec mprage atlas mask outdir [labels [labels ...]]
~~~

Let's chat about the things that might look a little funny here. `mask` is a binary mask (i.e. black and white) image of the brain in the atlas you're using. `outdir` is the base directory where you want your output files to be stored - don't worry, **ndmg** will handle the naming and organization within. Lastly, notice that `[labels [labels ...]]` block at the end? That means that **ndmg** allows you to make connectomes on multiple scales and parcellation schemes at once, you just need to pass in all of the sets of labels you'd like to use!

### Waiting for your results
The **ndmg** end-to-end pipeline takes about 30 minutes to run on my computer (a pretty basic Macbook), and feeds you output statements along the way.

### Diving deeper
Sure, the above gave you a taste of what the **ndmg** package can do, but what if you want a bit more of an intimiate knowledge of the inner workings of that pipeline we just showed? Well, you're in luck! Check out this [Jupyter Notebook]() that walks you through what the pipeline you just ran is doing.

### Questions?
If you're having trouble, notice a bug, or want to contribute (such as a fix to the bug you may have just found) feel free to open a git issue or pull request. Enjoy!