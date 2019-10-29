# !/usr/bin/env python

"""
ndmg.utils.gen_utils
~~~~~~~~~~~~~~~~~~~~

Contains general utility functions.
"""

# system imports
import os
import sys
import re
from subprocess import Popen, PIPE
import subprocess
import functools
from itertools import product
from pathlib import Path

# package imports
import bids
import numpy as np
import nibabel as nib
from nilearn.image import mean_img
from scipy.sparse import lil_matrix
from fury import actor
from fury import window

import dipy
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.align.reslice import reslice


class NameResource:
    """
    A class for naming derivatives under the BIDs spec.

    Parameters
    ----------
    modf : str
        Path to subject MRI (dwi) data to be analyzed
    t1wf : str
        Path to subject t1w anatomical data
    tempf : str
        Path to atlas file(s) to be used during analysis
    opath : str
        Path to output directory
    """

    def __init__(self, modf, t1wf, tempf, opath):
        """__init__ containing relevant BIDS specified paths for relevant data
        """
        self.__subi__ = os.path.basename(modf).split(".")[0]
        self.__anati__ = os.path.basename(t1wf).split(".")[0]
        self.__suball__ = ""
        self.__sub__ = re.search(r"(sub-)(?!.*sub-).*?(?=[_])", modf)
        if self.__sub__:
            self.__sub__ = self.__sub__.group()
            self.__suball__ = "sub-{}".format(self.__sub__)
        self.__ses__ = re.search(r"(ses-)(?!.*ses-).*?(?=[_])", modf)
        if self.__ses__:
            self.__ses__ = self.__ses__.group()
            self.__suball__ = self.__suball__ + "_ses-{}".format(self.__ses__)
        self.__run__ = re.search(r"(run-)(?!.*run-).*?(?=[_])", modf)
        if self.__run__:
            self.__run__ = self.__run__.group()
            self.__suball__ = self.__suball__ + "_run-{}".format(self.__run__)
        self.__task__ = re.search(r"(task-)(?!.*task-).*?(?=[_])", modf)
        if self.__task__:
            self.__task__ = self.__task__.group()
            self.__suball__ = self.__suball__ + "_run-{}".format(self.__task__)
        self.__temp__ = os.path.basename(tempf).split(".")[0]
        self.__space__ = re.split(r"[._]", self.__temp__)[0]
        self.__res__ = re.search(r"(res-)(?!.*res-).*?(?=[_])", tempf)
        if self.__res__:
            self.__res__ = self.__res__.group()
        self.__basepath__ = opath
        self.__outdir__ = self._get_outdir()
        return

    def add_dirs(namer, paths, labels, label_dirs):
        """Creates tmp and permanent directories for the desired suffixes

        Parameters
        ----------
        namer : NameResource
            varibale of the NameResource class created by NameResource() containing path and settings information for the desired run. It includes: subject, anatomical scan, session, run number, task, resolution, output directory
        paths : dict
            a dictionary of keys to suffix directories
        labels : list
            list of paths of all the atlas label nifti files being used (each will get their own directory)
        label_dirs : list
            list containing the keys from 'paths' you wish to add label level granularity to (create a directory for each value in 'labels')
        """

        namer.dirs = {}
        if not isinstance(labels, list):
            labels = [labels]
        dirtypes = ["output"]
        for dirt in dirtypes:
            olist = [namer.get_outdir()]
            namer.dirs[dirt] = {}
            if dirt in ["tmp"]:
                olist = olist + [dirt]
            namer.dirs[dirt]["base"] = os.path.join(*olist)
            for kwd, path in paths.items():
                newdir = os.path.join(*[namer.dirs[dirt]["base"], path])
                if kwd in label_dirs:  # levels with label granularity
                    namer.dirs[dirt][kwd] = {}
                    for label in labels:
                        labname = namer.get_label(label)
                        namer.dirs[dirt][kwd][labname] = os.path.join(newdir, labname)
                else:
                    namer.dirs[dirt][kwd] = newdir
        namer.dirs["tmp"] = {}
        namer.dirs["tmp"]["base"] = namer.get_outdir() + "/tmp"
        namer.dirs["tmp"]["reg_a"] = namer.dirs["tmp"]["base"] + "/reg_a"
        namer.dirs["tmp"]["reg_m"] = namer.dirs["tmp"]["base"] + "/reg_m"
        namer.dirs["qa"] = {}
        namer.dirs["qa"]["base"] = namer.get_outdir() + "/qa"
        namer.dirs["qa"]["adjacency"] = namer.dirs["qa"]["base"] + "/adjacency"
        namer.dirs["qa"]["fibers"] = namer.dirs["qa"]["base"] + "/fibers"
        namer.dirs["qa"]["graphs"] = namer.dirs["qa"]["base"] + "/graphs"
        namer.dirs["qa"]["graphs_plotting"] = (
            namer.dirs["qa"]["base"] + "/graphs_plotting"
        )
        namer.dirs["qa"]["mri"] = namer.dirs["qa"]["base"] + "/mri"
        namer.dirs["qa"]["reg"] = namer.dirs["qa"]["base"] + "/reg"
        namer.dirs["qa"]["tensor"] = namer.dirs["qa"]["base"] + "/tensor"
        newdirs = flatten(namer.dirs, [])
        cmd = "mkdir -p {}".format(" ".join(newdirs))
        execute_cmd(cmd)  # make the directories
        return

    def _get_outdir(self):
        """Called by constructor to initialize the output directory

        Returns
        -------
        list
            path to output directory
        """

        olist = [self.__basepath__]
        # olist.append(self.__sub__)
        # if self.__ses__:
        #    olist.append(self.__ses__)
        return os.path.join(*olist)

    def get_outdir(self):
        """Returns the base output directory for a particular subject and appropriate granularity.

        Returns
        -------
        str
            output directory
        """

        return self.__outdir__

    def get_label(self, label):
        """Return the formatted label information for the parcellation (i.e. the name of the file without the path)

        Parameters
        ----------
        label : str
            Path to parcellation file that you want the isolated name of

        Returns
        -------
        str
            the isolated file name
        """
        return get_filename(label)
        # return "label-{}".format(re.split(r'[._]',
        #                         os.path.basename(label))[0])

    def name_derivative(self, folder, derivative):
        """Creates derivative output file paths using os.path.join

        Parameters
        ----------
        folder : str
            Path of directory that you want the derivative file name appended too
        derivative : str
            The name of the file to be produced

        Returns
        -------
        str
            Derivative output file path
        """

        return os.path.join(*[folder, derivative])

    def get_mod_source(self):
        return self.__subi__

    def get_anat_source(self):
        return self.__anati__

    def get_sub_info(self):
        olist = []
        if self.__sub__:
            olist.append(self.__sub__)
        if self.__ses__:
            olist.append(self.__ses__)
        return olist


def flatten(current, result=[]):
    """Flatten a folder heirarchy

    Parameters
    ----------
    current : dict
        path to directory you want to flatten
    result : list, optional
        Used to store directory information between iterations of flatten, Default is []

    Returns
    -------
    list
        All new directories created by flattening the current directory
    """
    if isinstance(current, dict):
        for key in current:
            flatten(current[key], result)
    else:
        result.append(current)
    return result


class DirectorySweeper:
    # TODO : find data with run_label in it and test on that
    def __init__(self, bdir, subjs=None, seshs=None):
        self.layout = bids.BIDSLayout(bdir)
        self.bdir = bdir
        self.subjs = subjs
        self.seshs = seshs
        self.df = self.layout.to_df()
        self.trim()

    @staticmethod
    def all_strings(iterable):
        return [str(x) for x in iterable]

    def clean(self, iterable):
        iterable = as_list(iterable)
        iterable = self.all_strings(iterable)
        return iterable

    def trim(self):
        if self.subjs is not None:
            subjs = self.clean(self.subjs)
            self.df = self.df[self.df.subject.isin(subjs)]

        if self.seshs is not None:
            seshs = self.clean(self.seshs)
            self.df = self.df[self.df.session.isin(seshs)]

    def get(self, datatype=None, extension=None):
        df = self.df[(self.df.datatype == datatype) & (self.df.extension == extension)]
        return list(df.path)

    def get_dwis(self):
        return self.get(datatype="dwi", extension="nii.gz")

    def get_bvals(self):
        return self.get(datatype="dwi", extension="bval")

    def get_bvecs(self):
        return self.get(datatype="dwi", extension="bvec")

    def get_anats(self):
        return self.get(datatype="anat", extension="nii.gz")


# def sweep_directory(bdir, subj=None, sesh=None, task=None, run=None, modality="dwi"):
#     """Given a BIDs formatted directory, crawls the BIDs dir and prepares the necessary inputs for the NDMG pipeline. Uses regexes to check matches for BIDs compliance.

#     Parameters
#     ----------
#     bdir : str
#         input directory
#     subj : list, optional
#         subject label. Default = None
#     sesh : list, optional
#         session label. Default = None
#     task : list, optional
#         task label. Default = None
#     run : list, optional
#         run label. Default = None
#     modality : str, optional
#         Data type being analyzed. Default = "dwi"

#     Returns
#     -------
#     tuple
#         contining location of dwi, bval, bvec, and anat

#     Raises
#     ------
#     ValueError
#         Raised if incorrect mobility passed
#     """

#     dwis = []
#     bvals = []
#     bvecs = []
#     anats = []
#     layout = bids.BIDSLayout(bdir)  # initialize BIDs tree on bdir
#     # get all files matching the specific modality we are using
#     if subj is None:
#         subjs = layout.get_subjects()  # list of all the subjects
#     else:
#         subjs = as_list(subj)  # make it a list so we can iterate
#     for sub in subjs:
#         if not sesh:
#             seshs = layout.get_sessions(subject=sub)
#             seshs += [None]  # in case there are non-session level inputs
#         else:
#             seshs = as_list(sesh)  # make a list so we can iterate

#         if not task:
#             tasks = layout.get_tasks(subject=sub)
#             tasks += [None]
#         else:
#             tasks = as_list(task)

#         if not run:
#             runs = layout.get_runs(subject=sub)
#             runs += [None]
#         else:
#             runs = as_list(run)

#         print(f"Subject: {sub}")
#         print(f"Sessions: {seshs}")
#         print(f"Tasks: {tasks}")
#         print(f"Runs: {runs}")
#         print("\n\n")
#         # all the combinations of sessions and tasks that are possible
#         for (ses, tas, ru) in product(seshs, tasks, runs):
#             # the attributes for our modality img
#             mod_attributes = [sub, ses, tas, ru]
#             # the keys for our modality img
#             mod_keys = ["subject", "session", "task", "run"]
#             # our query we will use for each modality img
#             mod_query = {"modality": modality}
#             type_img = "dwi"  # use the dwi image
#             mod_query["suffix"] = type_img

#             for attr, key in zip(mod_attributes, mod_keys):
#                 if attr:
#                     mod_query[key] = attr

#             anat_attributes = [sub, ses]  # the attributes for our anat img
#             anat_keys = ["subject", "session"]  # the keys for our modality img
#             # our query for the anatomical image
#             anat_query = {
#                 "modality": "anat",
#                 "suffix": "T1w",
#                 "extensions": "nii.gz|nii",
#             }
#             for attr, key in zip(anat_attributes, anat_keys):
#                 if attr:
#                     anat_query[key] = attr
#             # make a query to fine the desired files from the BIDSLayout
#             anat = layout.get(**anat_query)
#             dwi = layout.get(**merge_dicts(mod_query, {"extensions": "nii.gz|nii"}))
#             bval = layout.get(**merge_dicts(mod_query, {"extensions": "bval"}))
#             bvec = layout.get(**merge_dicts(mod_query, {"extensions": "bvec"}))
#             if anat and dwi and bval and bvec:
#                 for (dw, bva, bve) in zip(dwi, bval, bvec):
#                     if dw.filename not in dwis:
#                         # if all the required files exist, append by the first
#                         # match (0 index)
#                         anats.append(anat[0].filename)
#                         dwis.append(dw.filename)
#                         bvals.append(bva.filename)
#                         bvecs.append(bve.filename)
#     if not len(dwis) or not len(bvals) or not len(bvecs) or not len(anats):
#         print("No dMRI files found in BIDs spec. Skipping...")
#     return (dwis, bvals, bvecs, anats)


def as_list(x):
    """A function to convert an item to a list if it is not, or pass it through otherwise

    Parameters
    ----------
    x : any object
        anything that can be entered into a list that you want to be converted into a list

    Returns
    -------
    list
        a list containing x
    """

    if isinstance(x, list):
        return x

    return [x]


def merge_dicts(x, y):
    """A function to merge two dictionaries, making it easier for us to make modality specific queries
    for dwi images (since they have variable extensions due to having an nii.gz, bval, and bvec file)

    Parameters
    ----------
    x : dict
        dictionary you want merged with y
    y : dict
        dictionary you want merged with x

    Returns
    -------
    dict
        combined dictionary with {x content,y content}
    """

    z = x.copy()
    z.update(y)
    return z


def check_exists(*dargs):
    """
    Decorator. For every integer index passed to check_exists,
    checks if the argument passed to that index in the function decorated contains a filepath that exists.
    Also standardizes print statements across functions.

    Parameters
    ----------
    dargs : ints
        Where to check the function being decorated for files.

    Raises
    ------
    ValueError
        Raised if the file at that location doesn't exist.

    Returns
    -------
    func
        dictionary of output files
    """

    def outer(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):

            for darg in dargs:
                p = args[darg]
                try:
                    if not os.path.exists(p):
                        raise ValueError(
                            f"{p} does not exist.\nThis is an input to the function {f.__name__}."
                        )
                except TypeError:
                    print(
                        f"{darg} is not a file, it is {type(darg)}. \nFix decorator on this function."
                    )

                print(f"{p} exists.")
            print(
                f"Prerequisite files for {f.__name__} all exist. Calling {f.__name__}."
            )
            print("\n")

            return f(*args, **kwargs)

        return inner

    return outer


def is_bids(input_dir):
    # TODO : change pybids dependency
    """
    Make sure that the input data is BIDs-formatted.
    If it's BIDs-formatted, except for a `dataset_description.json` file, return True.
    
    Returns
    -------
    bool
        True if the input directory is BIDs-formatted
    
    Raises
    ------
    ValueError
        Occurs if the input directory is not formatted properly.
    """
    try:
        l = bids.BIDSLayout(input_dir)
        return l.validate
    except ValueError as e:
        p = "'dataset_description.json' is missing from project root. Every valid BIDS dataset must have this file."
        if str(e) != p:
            raise ValueError(e)
        create_datadescript(input_dir)
        return is_bids(input_dir)


def create_datadescript(input_dir):
    """
    Creates a simple `data_description.json` file in the root of the input directory. Necessary for proper BIDs formatting.
    
    Parameters
    ----------
    input_dir : str
        BIDs-formatted input director.
    """
    print(f"Creating a simple dataset_description.json in {input_dir}... ")
    name = Path(input_dir).stem
    vers = bids.__version__
    out = dict(Name=name, BIDSVersion=vers)
    with open(input_dir + "/dataset_description.json", "w") as f:
        json.dump(out, f)


def check_dependencies():
    """
    Check for the existence of FSL and AFNI.
    Stop the pipeline immediately if these dependencies are not installed.

    Raises
    ------
    AssertionError
        Raised if FSL is not installed.
    AssertionError
        Raised if AFNI is not installed.
    """

    # Check for python version
    print(f"Python location : {sys.executable}")
    print(f"Python version : {sys.version}")
    print(f"DiPy version : {dipy.__version__}")
    if sys.version_info[0] < 3:
        warnings.warn(
            "WARNING : Using python 2. This Python version is no longer maintained. Use at your own risk."
        )

    # Check FSL installation
    try:
        print(f"Your fsl directory is located here: {os.environ['FSLDIR']}")
    except KeyError:
        raise AssertionError(
            "You do not have FSL installed! See installation instructions here: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation"
        )

    # Check AFNI installation
    try:
        print(
            f"Your AFNI directory is located here: {subprocess.check_output('which afni', shell=True, universal_newlines=True)}"
        )
    except subprocess.CalledProcessError:
        raise AssertionError(
            "You do not have AFNI installed! See installation instructions here: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/main_toc.html"
        )


def show_template_bundles(final_streamlines, template_path, fname):
    """Displayes the template bundles

    Parameters
    ----------
    final_streamlines : list
        Generated streamlines
    template_path : str
        Path to reference FA nii.gz file
    fname : str
        Path of the output file (saved as )
    """

    renderer = window.Renderer()
    template_img_data = nib.load(template_path).get_data().astype("bool")
    template_actor = actor.contour_from_roi(
        template_img_data, color=(50, 50, 50), opacity=0.05
    )
    renderer.add(template_actor)
    lines_actor = actor.streamtube(
        final_streamlines, window.colors.orange, linewidth=0.3
    )
    renderer.add(lines_actor)
    window.record(renderer, n_frames=1, out_path=fname, size=(900, 900))
    return


def execute_cmd(cmd, verb=False):
    """Given a bash command, it is executed and the response piped back to the
    calling script

    Parameters
    ----------
    cmd : str
        command you want to execute
    verb : bool, optional
        whether to print the command that is being executed, by default False

    Returns
    -------
    stdout
        outputs from p.communicate
    stderr
        error from p.communicate
    """

    if verb:
        print("Executing: {}".format(cmd))

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    code = p.returncode
    if code:
        sys.exit("Error {}: {}".format(code, err))
    return out, err


def get_braindata(brain_file):
    """Opens a brain data series for a mask, mri image, or atlas.
    Returns a numpy.ndarray representation of a brain.

    Parameters
    ----------
    brain_file : str, nibabel.nifti1.nifti1image, numpy.ndarray
        an object to open the data for a brain. Can be a string (path to a brain file),
        nibabel.nifti1.nifti1image, or a numpy.ndarray

    Returns
    -------
    array
        array of image data

    Raises
    ------
    TypeError
        Brain file is not an accepted format
    """

    if type(brain_file) is np.ndarray:  # if brain passed as matrix
        braindata = brain_file
    else:
        if type(brain_file) is str or type(brain_file) is str:
            brain = nib.load(str(brain_file))
        elif type(brain_file) is nib.nifti1.Nifti1Image:
            brain = brain_file
        else:
            raise TypeError(
                "Brain file is type: {}".format(type(brain_file))
                + "; accepted types are numpy.ndarray, "
                "string, and nibabel.nifti1.Nifti1Image."
            )
        braindata = brain.get_data()
    return braindata


def get_filename(path):
    """Given a fully qualified path, return just the file name, without extension

    Parameters
    ----------
    path : str
        Path to file you want isolated

    Returns
    -------
    str
        File name
    """
    return os.path.basename(path).split(".")[0]


def get_slice(mri, volid, sli):
    """Takes a volume index and constructs a new nifti image from the specified volume

    Parameters
    ----------
    mri : str
        Path to the 4d mri volume you wish to extract a slice from
    volid : int
        The index of the volume desired
    sli : str
        Path for the resulting file containing the desired slice
    """

    mri_im = nib.load(mri)
    data = mri_im.get_data()
    # get the slice at the desired volume
    vol = np.squeeze(data[:, :, :, volid])

    # Wraps volume in new nifti image
    head = mri_im.get_header()
    head.set_data_shape(head.get_data_shape()[0:3])
    out = nib.Nifti1Image(vol, affine=mri_im.get_affine(), header=head)
    out.update_header()
    # and saved to a new file
    nib.save(out, sli)


def make_gtab_and_bmask(fbval, fbvec, dwi_file, outdir):
    """Takes bval and bvec files and produces a structure in dipy format while also using FSL commands

    Parameters
    ----------
    fbval : str
        Path to b-value file
    fbvec : str
        Path to b-vector file
    dwi_file : str
        Path to dwi file being analyzed
    outdir : str
        output directory

    Returns
    -------
    GradientTable
        gradient table created from bval and bvec files
    str
        location of averaged b0 image file
    str
        location of b0 brain mask file
    """

    # Use B0's from the DWI to create a more stable DWI image for registration
    nodif_B0 = "{}/nodif_B0.nii.gz".format(outdir)
    nodif_B0_bet = "{}/nodif_B0_bet.nii.gz".format(outdir)
    nodif_B0_mask = "{}/nodif_B0_bet_mask.nii.gz".format(outdir)

    # loading bvecs/bvals
    print(fbval)
    print(fbvec)
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

    # Creating the gradient table
    gtab = gradient_table(bvals, bvecs, atol=1.0)

    # Correct b0 threshold
    gtab.b0_threshold = min(bvals)

    # Get B0 indices
    B0s = np.where(gtab.bvals == gtab.b0_threshold)[0]
    print("%s%s" % ("B0's found at: ", B0s))

    # Show info
    print(gtab.info)

    # Extract and Combine all B0s collected
    print("Extracting B0's...")
    cmds = []
    B0s_bbr = []
    for B0 in B0s:
        print(B0)
        B0_bbr = "{}/{}_B0.nii.gz".format(outdir, str(B0))
        cmd = "fslroi " + dwi_file + " " + B0_bbr + " " + str(B0) + " 1"
        cmds.append(cmd)
        B0s_bbr.append(B0_bbr)

    for cmd in cmds:
        print(cmd)
        os.system(cmd)

    # Get mean B0
    B0s_bbr_imgs = []
    for B0 in B0s_bbr:
        B0s_bbr_imgs.append(nib.load(B0))

    mean_B0 = mean_img(B0s_bbr_imgs)
    nib.save(mean_B0, nodif_B0)

    # Get mean B0 brain mask
    cmd = "bet " + nodif_B0 + " " + nodif_B0_bet + " -m -f 0.2"
    os.system(cmd)
    return gtab, nodif_B0, nodif_B0_mask


def normalize_xform(img):
    """ Set identical, valid qform and sform matrices in an image
    Selects the best available affine (sform > qform > shape-based), and
    coerces it to be qform-compatible (no shears).
    The resulting image represents this same affine as both qform and sform,
    and is marked as NIFTI_XFORM_ALIGNED_ANAT, indicating that it is valid,
    not aligned to template, and not necessarily preserving the original
    coordinates.
    If header would be unchanged, returns input image.

    Parameters
    ----------
    img : Nifti1Image
        Input image to be normalized

    Returns
    -------
    Nifti1Image
        normalized image
    """

    # Let nibabel convert from affine to quaternions, and recover xform
    tmp_header = img.header.copy()
    tmp_header.set_qform(img.affine)
    xform = tmp_header.get_qform()
    xform_code = 2

    # Check desired codes
    qform, qform_code = img.get_qform(coded=True)
    sform, sform_code = img.get_sform(coded=True)
    if all(
        (
            qform is not None and np.allclose(qform, xform),
            sform is not None and np.allclose(sform, xform),
            int(qform_code) == xform_code,
            int(sform_code) == xform_code,
        )
    ):
        return img

    new_img = img.__class__(img.get_data(), xform, img.header)
    # Unconditionally set sform/qform
    new_img.set_sform(xform, xform_code)
    new_img.set_qform(xform, xform_code)

    return new_img


def reorient_dwi(dwi_prep, bvecs, namer):
    """Orients dwi data to the proper orientation (RAS+) using nibabel

    Parameters
    ----------
    dwi_prep : str
        Path to eddy corrected dwi file
    bvecs : str
        Path to the resaled b-vector file
    namer : NameResource
        NameResource variable containing relevant directory tree information

    Returns
    -------
    str
        Path to potentially reoriented dwi file
    str
        Path to b-vector file, potentially reoriented if dwi data was
    """

    fname = dwi_prep
    bvec_fname = bvecs
    out_bvec_fname = "%s%s" % (namer.dirs["output"]["prep_dwi"], "/bvecs_reor.bvec")

    input_img = nib.load(fname)
    input_axcodes = nib.aff2axcodes(input_img.affine)
    reoriented = nib.as_closest_canonical(input_img)
    normalized = normalize_xform(reoriented)
    # Is the input image oriented how we want?
    new_axcodes = ("R", "A", "S")
    if normalized is not input_img:
        out_fname = "%s%s%s%s" % (
            namer.dirs["output"]["prep_dwi"],
            "/",
            dwi_prep.split("/")[-1].split(".nii.gz")[0],
            "_reor_RAS.nii.gz",
        )
        print("%s%s%s" % ("Reorienting ", dwi_prep, " to RAS+..."))

        # Flip the bvecs
        input_orientation = nib.orientations.axcodes2ornt(input_axcodes)
        desired_orientation = nib.orientations.axcodes2ornt(new_axcodes)
        transform_orientation = nib.orientations.ornt_transform(
            input_orientation, desired_orientation
        )
        bvec_array = np.loadtxt(bvec_fname)
        if bvec_array.shape[0] != 3:
            bvec_array = bvec_array.T
        if not bvec_array.shape[0] == transform_orientation.shape[0]:
            raise ValueError("Unrecognized bvec format")
        output_array = np.zeros_like(bvec_array)
        for this_axnum, (axnum, flip) in enumerate(transform_orientation):
            output_array[this_axnum] = bvec_array[int(axnum)] * float(flip)
        np.savetxt(out_bvec_fname, output_array, fmt="%.8f ")
    else:
        out_fname = "%s%s%s%s" % (
            namer.dirs["output"]["prep_dwi"],
            "/",
            dwi_prep.split("/")[-1].split(".nii.gz")[0],
            "_RAS.nii.gz",
        )
        out_bvec_fname = bvec_fname

    normalized.to_filename(out_fname)

    return out_fname, out_bvec_fname


def reorient_img(img, namer):
    """Reorients input image to RAS+

    Parameters
    ----------
    img : str
        Path to image being reoriented
    namer : NameResource
        NameResource object containing all revlevent pathing information for the pipeline

    Returns
    -------
    str
        Path to reoriented image
    """

    # Load image, orient as RAS
    orig_img = nib.load(img)
    reoriented = nib.as_closest_canonical(orig_img)
    normalized = normalize_xform(reoriented)

    # Image may be reoriented
    if normalized is not orig_img:
        print("%s%s%s" % ("Reorienting ", img, " to RAS+..."))
        out_name = "%s%s%s%s" % (
            namer.dirs["output"]["prep_anat"],
            "/",
            img.split("/")[-1].split(".nii.gz")[0],
            "_reor_RAS.nii.gz",
        )
    else:
        out_name = "%s%s%s%s" % (
            namer.dirs["output"]["prep_anat"],
            "/",
            img.split("/")[-1].split(".nii.gz")[0],
            "_RAS.nii.gz",
        )

    normalized.to_filename(out_name)

    return out_name


def match_target_vox_res(img_file, vox_size, namer, sens):
    """Reslices input MRI file if it does not match the targeted voxel resolution. Can take dwi or t1w scans.

    Parameters
    ----------
    img_file : str
        path to file to be resliced
    vox_size : str
        target voxel resolution ('2mm' or '1mm')
    namer : NameResource
        NameResource variable containing relevant directory tree information
    sens : str
        type of data being analyzed ('dwi' or 'func')

    Returns
    -------
    str
        location of potentially resliced image
    """

    # Check dimensions
    img = nib.load(img_file)
    data = img.get_fdata()
    affine = img.affine
    hdr = img.header
    zooms = hdr.get_zooms()[:3]
    if vox_size == "1mm":
        new_zooms = (1.0, 1.0, 1.0)
    elif vox_size == "2mm":
        new_zooms = (2.0, 2.0, 2.0)

    if (abs(zooms[0]), abs(zooms[1]), abs(zooms[2])) != new_zooms:
        print("Reslicing image " + img_file + " to " + vox_size + "...")
        if sens == "dwi":
            img_file_res = "%s%s%s%s" % (
                namer.dirs["output"]["prep_dwi"],
                "/",
                os.path.basename(img_file).split(".nii.gz")[0],
                "_res.nii.gz",
            )
        elif sens == "t1w":
            img_file_res = "%s%s%s%s" % (
                namer.dirs["output"]["prep_anat"],
                "/",
                os.path.basename(img_file).split(".nii.gz")[0],
                "_res.nii.gz",
            )

        data2, affine2 = reslice(data, affine, zooms, new_zooms)
        img2 = nib.Nifti1Image(data2, affine=affine2)
        nib.save(img2, img_file_res)
        img_file = img_file_res
    else:
        print("Reslicing image " + img_file + " to " + vox_size + "...")
        if sens == "dwi":
            img_file_nores = "%s%s%s%s" % (
                namer.dirs["output"]["prep_dwi"],
                "/",
                os.path.basename(img_file).split(".nii.gz")[0],
                "_nores.nii.gz",
            )
        elif sens == "t1w":
            img_file_nores = "%s%s%s%s" % (
                namer.dirs["output"]["prep_anat"],
                "/",
                os.path.basename(img_file).split(".nii.gz")[0],
                "_nores.nii.gz",
            )
        nib.save(img, img_file_nores)
        img_file = img_file_nores

    return img_file


def parcel_overlap(parcellation1, parcellation2, outpath):
    """A function to compute the percent composition of each parcel in
    parcellation 1 with the parcels in parcellation 2. Rows are indices
    in parcellation 1; cols are parcels in parcellation 2. Values are the
    percent of voxels in parcel (parcellation 1) that fall into parcel
    (parcellation 2). Implied is that each row sums to 1.

    Parameters
    ----------
    parcellation1 : str
        the path to the first parcellation.
    parcellation2 : str
        the path to the second parcellation.
    outpath : str
        the path to produce the output.
    """

    p1_dat = nib.load(parcellation1).get_data()
    p2_dat = nib.load(parcellation2).get_data()
    p1regs = np.unique(p1_dat)
    p1regs = p1regs[p1regs > 0]
    p2regs = np.unique(p2_dat)

    p1n = get_filename(parcellation1)
    p2n = get_filename(parcellation2)

    overlapdat = lil_matrix((p1regs.shape[0], p2regs.shape[0]), dtype=np.float32)
    for p1idx, p1reg in enumerate(p1regs):
        p1seq = p1_dat == p1reg
        N = p1seq.sum()
        poss_regs = np.unique(p2_dat[p1seq])
        for p2idx, p2reg in enumerate(p2regs):
            if p2reg in poss_regs:
                # percent overlap is p1seq and'd with the anatomical region voxelspace, summed and normalized
                pover = np.logical_and(p1seq, p2_dat == p2reg).sum() / float(N)
                overlapdat[p1idx, p2idx] = pover

    outf = os.path.join(outpath, "{}_{}.csv".format(p1n, p2n))
    with open(outf, "w") as f:
        p2str = ["%s" % x for x in p2regs]
        f.write("p1reg," + ",".join(p2str) + "\n")
        for idx, p1reg in enumerate(p1regs):
            datstr = ["%.4f" % x for x in overlapdat[idx,].toarray()[0,]]
            f.write(str(p1reg) + "," + ",".join(datstr) + "\n")
        f.close()
