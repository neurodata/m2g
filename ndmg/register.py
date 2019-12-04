#!/usr/bin/env python

"""
ndmg.register
~~~~~~~~~~~~~
Contains ndmg's registration classes, organized as full registration workflows.
Used for the majority of the registration described here: https://neurodata.io/talks/ndmg.pdf#page=20
"""

# standard library imports
import os

# package imports
import nibabel as nib
import numpy as np
from nilearn.image import load_img
from nilearn.image import math_img
from dipy.tracking.streamline import deform_streamlines
from dipy.io.streamline import load_trk
from dipy.tracking import utils

# ndmg imports
from ndmg.utils import gen_utils
from ndmg.utils import reg_utils
from ndmg.stats import qa_reg

@gen_utils.timer
def direct_streamline_norm(streams, fa_path, namer):
    """Applys the Symmetric Diffeomorphic Registration (SyN) Algorithm onto the streamlines to the atlas space defined by .../atlases/reference_brains/FSL_HCP1065_FA_2mm.nii.gz
    Parameters
    ----------
    streams : str
        Path to streamlines.trk file to be transformed
    fa_path : str
        Path to subject's FA tensor image
    namer : NameResource
        variable containing all relevant pathing information
    Returns
    -------
    ArraySequence
        Transformed streamlines
    str
        Path to tractogram streamline file: streamlines_dsn.trk
    """

    # TODO : put this atlas stuff into a function
    if os.path.isdir("/ndmg_atlases"):
        # in docker
        atlas_dir = "/ndmg_atlases"
    else:
        # local
        atlas_dir = os.path.expanduser("~") + "/.ndmg/ndmg_atlases"

    template_path = atlas_dir + "/atlases/reference_brains/FSL_HCP1065_FA_2mm.nii.gz"

    streams_warp_png = namer.dirs["tmp"]["base"] + "/warp_qc.png"

    # Run SyN and normalize streamlines
    fa_img = nib.load(fa_path)
    vox_size = fa_img.get_header().get_zooms()[0]
    template_img = nib.load(template_path)
    template_data = template_img.get_data()

    # SyN FA->Template
    [mapping, affine_map] = reg_utils.wm_syn(
        template_path, fa_path, namer.dirs["tmp"]["base"]
    )
    streamlines = load_trk(streams, reference="same")

    # Warp streamlines
    adjusted_affine = affine_map.affine.copy()
    adjusted_affine[1][3] = -adjusted_affine[1][3] / vox_size ** 2
    mni_streamlines = deform_streamlines(
        streamlines.streamlines,
        deform_field=mapping.get_forward_field()[-1:],
        stream_to_current_grid=template_img.affine,
        current_grid_to_world=adjusted_affine,
        stream_to_ref_grid=template_img.affine,
        ref_grid_to_world=np.eye(4),
    )

    # Save streamlines
    hdr = fa_img.header
    trk_affine = np.eye(4)
    trk_hdr = nib.streamlines.trk.TrkFile.create_empty_header()
    trk_hdr["hdr_size"] = 1000
    trk_hdr["dimensions"] = hdr["dim"][1:4].astype("float32")
    trk_hdr["voxel_sizes"] = hdr["pixdim"][1:4]
    trk_hdr["voxel_to_rasmm"] = trk_affine
    trk_hdr["voxel_order"] = "RAS"
    trk_hdr["pad2"] = "RAS"
    trk_hdr["image_orientation_patient"] = np.array(
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ).astype("float32")
    trk_hdr["endianness"] = "<"
    trk_hdr["_offset_data"] = 1000
    trk_hdr["nb_streamlines"] = len(mni_streamlines)
    tractogram = nib.streamlines.Tractogram(mni_streamlines, affine_to_rasmm=trk_affine)
    trkfile = nib.streamlines.trk.TrkFile(tractogram, header=trk_hdr)
    streams_mni = streams.split(".trk")[0] + "_dsn.trk"
    nib.streamlines.save(trkfile, streams_mni)

    # DSN QC plotting
    # gen_utils.show_template_bundles(mni_streamlines, template_path, streams_warp_png)

    return mni_streamlines, streams_mni


class DmriReg:
    """Class containing relevant paths and class methods for analysing tractography
    Parameters
    ----------
    namer : NameResource
        NameResource variable containing relevant directory tree information
    nodif_B0 : str
        path to mean b0 image
    nodif_B0_mask : str
        path to mean b0 mask (nodif_B0....nii.gz)
    t1w_in : str
        path to t1w file
    vox_size : str
        voxel resolution ('2mm' or '1mm')
    skull : str, optional
        skullstrip parameter pre-set. Default is "none"
    simple : bool, optional
        Whether you want to attempt non-linear registration when transforming between mni, t1w, and dwi space. Default is False
    Raises
    ------
    ValueError
        FSL atlas for ventricle reference not found
    """

    def __init__(
        self,
        namer,
        nodif_B0,
        nodif_B0_mask,
        t1w_in,
        vox_size,
        skull="none",
        simple=False,
    ):

        if os.path.isdir("/ndmg_atlases"):
            # in docker
            atlas_dir = "/ndmg_atlases"
        else:
            # local
            atlas_dir = os.path.expanduser("~") + "/.ndmg/ndmg_atlases"
        try:
            FSLDIR = os.environ["FSLDIR"]
        except KeyError:
            print("FSLDIR environment variable not set!")

        if vox_size == "2mm":
            vox_dims = "2x2x2"
        elif vox_size == "1mm":
            vox_dims = "1x1x1"

        self.simple = simple
        self.nodif_B0 = nodif_B0
        self.nodif_B0_mask = nodif_B0_mask
        self.t1w = t1w_in
        self.vox_size = vox_size
        self.t1w_name = "t1w"
        self.dwi_name = "dwi"
        self.namer = namer
        self.skull = skull
        self.t12mni_xfm_init = f'{self.namer.dirs["tmp"]["reg_m"]}/xfm_t1w2mni_init.mat'
        self.mni2t1_xfm_init = f'{self.namer.dirs["tmp"]["reg_m"]}/xfm_mni2t1w_init.mat'
        self.t12mni_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/xfm_t1w2mni.mat'
        self.mni2t1_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/xfm_mni2t1.mat'
        self.mni2t1w_warp = f'{self.namer.dirs["tmp"]["reg_a"]}/mni2t1w_warp.nii.gz'
        self.warp_t1w2mni = f'{self.namer.dirs["tmp"]["reg_a"]}/warp_t12mni.nii.gz'
        self.t1w2dwi = f'{self.namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_in_dwi.nii.gz'
        self.t1_aligned_mni = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_aligned_mni.nii.gz'
        self.t1w_brain = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_brain.nii.gz'
        self.dwi2t1w_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/dwi2t1w_xfm.mat'
        self.t1w2dwi_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/t1w2dwi_xfm.mat'
        self.t1w2dwi_bbr_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/t1w2dwi_bbr_xfm.mat'
        self.dwi2t1w_bbr_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/dwi2t1w_bbr_xfm.mat'
        self.t1wtissue2dwi_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/t1wtissue2dwi_xfm.mat'
        self.xfm_atlas2t1w_init = f'{self.namer.dirs["tmp"]["reg_m"]}/{self.t1w_name}_xfm_atlas2t1w_init.mat'
        self.xfm_atlas2t1w = f'{self.namer.dirs["tmp"]["reg_m"]}/{self.t1w_name}_xfm_atlas2t1w.mat'
        self.temp2dwi_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/{self.dwi_name}_xfm_temp2dwi.mat'

        self.input_mni = f'{FSLDIR}/data/standard/MNI152_T1_{vox_size}_brain.nii.gz'
        self.input_mni_mask = f'{FSLDIR}/data/standard/MNI152_T1_{vox_size}_brain_mask.nii.gz'
        self.temp2dwi_xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/{self.dwi_name}_xfm_temp2dwi.mat'
        self.map_path = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_seg'
        self.wm_mask = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_wm.nii.gz'
        self.wm_mask_thr = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_wm_thr.nii.gz'
        self.wm_edge = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.t1w_name}_wm_edge.nii.gz'
        self.csf_mask = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_csf.nii.gz'
        self.gm_mask = f'{self.namer.dirs["output"]["prep_anat"]}/{self.t1w_name}_gm.nii.gz'
        self.xfm_roi2mni_init = f'{self.namer.dirs["tmp"]["reg_m"]}/roi_2_mni.mat'
        self.lvent_out_file = f'{self.namer.dirs["tmp"]["reg_a"]}/LVentricle.nii.gz'
        self.rvent_out_file = f'{self.namer.dirs["tmp"]["reg_a"]}/RVentricle.nii.gz'
        self.csf_mask_dwi = f'{self.namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_csf_mask_dwi.nii.gz'
        self.gm_in_dwi = f'{self.namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_gm_in_dwi.nii.gz'
        self.wm_in_dwi = f'{self.namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_wm_in_dwi.nii.gz'
        self.csf_mask_dwi_bin = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.t1w_name}_csf_mask_dwi_bin.nii.gz'
        self.gm_in_dwi_bin = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.t1w_name}_gm_in_dwi_bin.nii.gz'
        self.wm_in_dwi_bin = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.t1w_name}_wm_in_dwi_bin.nii.gz'
        self.vent_mask_dwi = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.t1w_name}_vent_mask_dwi.nii.gz'
        self.vent_csf_in_dwi = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.t1w_name}_vent_csf_in_dwi.nii.gz'
        self.vent_mask_mni = f'{self.namer.dirs["tmp"]["reg_a"]}/vent_mask_mni.nii.gz'
        self.vent_mask_t1w = f'{self.namer.dirs["tmp"]["reg_a"]}/vent_mask_t1w.nii.gz'
        self.wm_gm_int_in_dwi = f'{namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_wm_gm_int_in_dwi.nii.gz'
        self.wm_gm_int_in_dwi_bin = f'{namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_wm_gm_int_in_dwi_bin.nii.gz'
        self.input_mni_sched = f'{FSLDIR}/etc/flirtsch/T1_2_MNI152_2mm.cnf'
        self.mni_atlas = f'{atlas_dir}/atlases/label/Human/HarvardOxfordsub-maxprob-thr25_space-MNI152NLin6_label_all_res-{vox_dims}.nii.gz'
        self.mni_vent_loc = f'{atlas_dir}/atlases/mask/HarvardOxford-thr25_space-MNI152NLin6_variant-lateral-ventricles_res-{vox_dims}_descr-brainmask.nii.gz'
        self.corpuscallosum = f'{atlas_dir}/atlases/mask/CorpusCallosum_res_{vox_size}.nii.gz'
        self.corpuscallosum_mask_t1w = f'{self.namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_corpuscallosum.nii.gz'
        self.corpuscallosum_dwi = f'{self.namer.dirs["output"]["reg_anat"]}/{self.t1w_name}_corpuscallosum_dwi.nii.gz'

    @gen_utils.timer
    def gen_tissue(self):
        """Extracts the brain from the raw t1w image (as indicated by self.t1w), uses it to create WM, GM, and CSF masks,
        reslices all 4 files to the target voxel resolution and extracts the white matter edge. Each mask is saved to
        location indicated by self.map_path
        """
        # BET needed for this, as afni 3dautomask only works on 4d volumes
        print("Extracting brain from raw T1w image...")
        reg_utils.t1w_skullstrip(self.t1w, self.t1w_brain, self.skull)

        # Segment the t1w brain into probability maps
        self.maps = reg_utils.segment_t1w(self.t1w_brain, self.map_path)
        self.wm_mask = self.maps["wm_prob"]
        self.gm_mask = self.maps["gm_prob"]
        self.csf_mask = self.maps["csf_prob"]

        self.t1w_brain = gen_utils.match_target_vox_res(
            self.t1w_brain, self.vox_size, self.namer, sens="t1w"
        )
        self.wm_mask = gen_utils.match_target_vox_res(
            self.wm_mask, self.vox_size, self.namer, sens="t1w"
        )
        self.gm_mask = gen_utils.match_target_vox_res(
            self.gm_mask, self.vox_size, self.namer, sens="t1w"
        )
        self.csf_mask = gen_utils.match_target_vox_res(
            self.csf_mask, self.vox_size, self.namer, sens="t1w"
        )

        # Threshold WM to binary in dwi space
        self.t_img = load_img(self.wm_mask)
        self.mask = math_img("img > 0.2", img=self.t_img)
        self.mask.to_filename(self.wm_mask_thr)

        # Extract wm edge
        cmd = f'fslmaths {self.wm_mask_thr} -edge -bin -mas {self.wm_mask_thr} {self.wm_edge}'
        print("Extracting white matter edge ...")
        print(cmd)
        os.system(cmd)


    @gen_utils.timer
    def t1w2dwi_align(self):
        """Alignment from t1w to mni, making t1w_mni, and t1w_mni to dwi. A function to perform self alignment. Uses a local optimisation cost function to get the
        two images close, and then uses bbr to obtain a good alignment of brain boundaries. Assumes input dwi is already preprocessed and brain extracted.
        """

        # Create linear transform/ initializer T1w-->MNI
        reg_utils.align(
            self.t1w_brain,
            self.input_mni,
            xfm=self.t12mni_xfm_init,
            bins=None,
            interp="spline",
            out=None,
            dof=12,
            cost="mutualinfo",
            searchrad=True,
        )

        # Attempt non-linear registration of T1 to MNI template
        if self.simple is False:
            try:
                print("Running non-linear registration: T1w-->MNI ...")
                # Use FNIRT to nonlinearly align T1 to MNI template
                reg_utils.align_nonlinear(
                    self.t1w_brain,
                    self.input_mni,
                    xfm=self.t12mni_xfm_init,
                    out=self.t1_aligned_mni,
                    warp=self.warp_t1w2mni,
                    ref_mask=self.input_mni_mask,
                    config=self.input_mni_sched,
                )

                # Get warp from MNI -> T1
                reg_utils.inverse_warp(
                    self.t1w_brain, self.mni2t1w_warp, self.warp_t1w2mni
                )

                # Get mat from MNI -> T1
                cmd = f'convert_xfm -omat {self.mni2t1_xfm_init} -inverse {self.t12mni_xfm_init}'
                print(cmd)
                os.system(cmd)

            except RuntimeError("Error: FNIRT failed!"):
                pass
        else:
            # Falling back to linear registration
            reg_utils.align(
                self.t1w_brain,
                self.input_mni,
                xfm=self.t12mni_xfm,
                init=self.t12mni_xfm_init,
                bins=None,
                dof=12,
                cost="mutualinfo",
                searchrad=True,
                interp="spline",
                out=self.t1_aligned_mni,
                sch=None,
            )
        qa_reg.reg_mri_pngs(self.t1_aligned_mni, self.input_mni, self.namer.dirs['qa']['reg'])

        # Align T1w-->DWI
        reg_utils.align(
            self.nodif_B0,
            self.t1w_brain,
            xfm=self.t1w2dwi_xfm,
            bins=None,
            interp="spline",
            dof=6,
            cost="mutualinfo",
            out=None,
            searchrad=True,
            sch=None,
        )
        cmd = f'convert_xfm -omat {self.dwi2t1w_xfm} -inverse {self.t1w2dwi_xfm}'
        print(cmd)
        os.system(cmd)

        if self.simple is False:
            # Flirt bbr
            try:
                print("Running FLIRT BBR registration: T1w-->DWI ...")
                reg_utils.align(
                    self.nodif_B0,
                    self.t1w_brain,
                    wmseg=self.wm_edge,
                    xfm=self.dwi2t1w_bbr_xfm,
                    init=self.dwi2t1w_xfm,
                    bins=256,
                    dof=7,
                    searchrad=True,
                    interp="spline",
                    out=None,
                    cost="bbr",
                    finesearch=5,
                    sch="${FSLDIR}/etc/flirtsch/bbr.sch",
                )
                cmd = f'convert_xfm -omat {self.t1w2dwi_bbr_xfm} -inverse {self.dwi2t1w_bbr_xfm}'
                os.system(cmd)

                # Apply the alignment
                reg_utils.align(
                    self.t1w_brain,
                    self.nodif_B0,
                    init=self.t1w2dwi_bbr_xfm,
                    xfm=self.t1wtissue2dwi_xfm,
                    bins=None,
                    interp="spline",
                    dof=7,
                    cost="mutualinfo",
                    out=self.t1w2dwi,
                    searchrad=True,
                    sch=None,
                )
            except RuntimeError("Error: FLIRT BBR failed!"):
                pass
        else:
            # Apply the alignment
            reg_utils.align(
                self.t1w_brain,
                self.nodif_B0,
                init=self.t1w2dwi_xfm,
                xfm=self.t1wtissue2dwi_xfm,
                bins=None,
                interp="spline",
                dof=6,
                cost="mutualinfo",
                out=self.t1w2dwi,
                searchrad=True,
                sch=None,
            )
        qa_reg.reg_mri_pngs(self.t1w2dwi, self.nodif_B0, self.namer.dirs['qa']['reg'])


    def atlas2t1w2dwi_align(self, atlas, dsn=True):
        """alignment from atlas to t1w to dwi. A function to perform atlas alignmet. Tries nonlinear registration first, and if that fails, does a liner
        registration instead.
        Note: for this to work, must first have called t1w2dwi_align.
        Parameters
        ----------
        atlas : str
            path to atlas file you want to use
        dsn : bool, optional
            is your space for tractography native-dsn, by default True
        Returns
        -------
        str
            path to aligned atlas file
        """

        self.atlas = atlas
        self.atlas_name = self.atlas.split("/")[-1].split(".")[0]
        self.aligned_atlas_t1mni = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.atlas_name}_aligned_atlas_t1w_mni.nii.gz'
        self.aligned_atlas_skull = f'{self.namer.dirs["tmp"]["reg_a"]}/{self.atlas_name}_aligned_atlas_skull.nii.gz'
        self.dwi_aligned_atlas = f'{self.namer.dirs["output"]["reg_anat"]}/{self.atlas_name}_aligned_atlas.nii.gz'
        # self.dwi_aligned_atlas_mask = "{}/{}_aligned_atlas_mask.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.atlas_name)

        reg_utils.align(
            self.atlas,
            self.t1_aligned_mni,
            init=None,
            xfm=None,
            out=self.aligned_atlas_t1mni,
            dof=12,
            searchrad=True,
            interp="nearestneighbour",
            cost="mutualinfo",
        )

        if (self.simple is False) and (dsn is False):
            try:
                # Apply warp resulting from the inverse of T1w-->MNI created earlier
                reg_utils.apply_warp(
                    self.t1w_brain,
                    self.aligned_atlas_t1mni,
                    self.aligned_atlas_skull,
                    warp=self.mni2t1w_warp,
                    interp="nn",
                    sup=True,
                )

                # Apply transform to dwi space
                reg_utils.align(
                    self.aligned_atlas_skull,
                    self.nodif_B0,
                    init=self.t1wtissue2dwi_xfm,
                    xfm=None,
                    out=self.dwi_aligned_atlas,
                    dof=6,
                    searchrad=True,
                    interp="nearestneighbour",
                    cost="mutualinfo",
                )
            except:
                print(
                    "Warning: Atlas is not in correct dimensions, or input is low quality,\nusing linear template registration."
                )
                # Create transform to align atlas to T1w using flirt
                reg_utils.align(
                    self.atlas,
                    self.t1w_brain,
                    xfm=self.xfm_atlas2t1w_init,
                    init=None,
                    bins=None,
                    dof=6,
                    cost="mutualinfo",
                    searchrad=True,
                    interp="spline",
                    out=None,
                    sch=None,
                )
                reg_utils.align(
                    self.atlas,
                    self.t1_aligned_mni,
                    xfm=self.xfm_atlas2t1w,
                    out=None,
                    dof=6,
                    searchrad=True,
                    bins=None,
                    interp="spline",
                    cost="mutualinfo",
                    init=self.xfm_atlas2t1w_init,
                )

                # Combine our linear transform from t1w to template with our transform from dwi to t1w space to get a transform from atlas ->(-> t1w ->)-> dwi
                reg_utils.combine_xfms(
                    self.xfm_atlas2t1w, self.t1wtissue2dwi_xfm, self.temp2dwi_xfm
                )

                # Apply linear transformation from template to dwi space
                reg_utils.applyxfm(
                    self.nodif_B0, self.atlas, self.temp2dwi_xfm, self.dwi_aligned_atlas
                )
        elif dsn is False:
            # Create transform to align atlas to T1w using flirt
            reg_utils.align(
                self.atlas,
                self.t1w_brain,
                xfm=self.xfm_atlas2t1w_init,
                init=None,
                bins=None,
                dof=6,
                cost="mutualinfo",
                searchrad=None,
                interp="spline",
                out=None,
                sch=None,
            )
            reg_utils.align(
                self.atlas,
                self.t1w_brain,
                xfm=self.xfm_atlas2t1w,
                out=None,
                dof=6,
                searchrad=True,
                bins=None,
                interp="spline",
                cost="mutualinfo",
                init=self.xfm_atlas2t1w_init,
            )

            # Combine our linear transform from t1w to template with our transform from dwi to t1w space to get a transform from atlas ->(-> t1w ->)-> dwi
            reg_utils.combine_xfms(
                self.xfm_atlas2t1w, self.t1wtissue2dwi_xfm, self.temp2dwi_xfm
            )

            # Apply linear transformation from template to dwi space
            reg_utils.applyxfm(
                self.nodif_B0, self.atlas, self.temp2dwi_xfm, self.dwi_aligned_atlas
            )
        else:
            pass

        # Set intensities to int
        if dsn is False:
            self.atlas_img = nib.load(self.dwi_aligned_atlas)
        else:
            self.atlas_img = nib.load(self.aligned_atlas_t1mni)
        self.atlas_data = np.around(self.atlas_img.get_data()).astype("int16")
        node_num = len(np.unique(self.atlas_data))
        self.atlas_data[self.atlas_data > node_num] = 0

        t_img = load_img(self.wm_gm_int_in_dwi)
        mask = math_img("img > 0", img=t_img)
        mask.to_filename(self.wm_gm_int_in_dwi_bin)

        if dsn is False:
            nib.save(
                nib.Nifti1Image(
                    self.atlas_data.astype(np.int32),
                    affine=self.atlas_img.affine,
                    header=self.atlas_img.header,
                ),
                self.dwi_aligned_atlas,
            )
            qa_reg.reg_mri_pngs(self.dwi_aligned_atlas, self.nodif_B0, self.namer.dirs['qa']['reg'])
            return self.dwi_aligned_atlas
        else:
            nib.save(
                nib.Nifti1Image(
                    self.atlas_data.astype(np.int32),
                    affine=self.atlas_img.affine,
                    header=self.atlas_img.header,
                ),
                self.aligned_atlas_t1mni,
            )
            qa_reg.reg_mri_pngs(self.aligned_atlas_t1mni, self.t1_aligned_mni, self.namer.dirs['qa']['reg'])
            return self.aligned_atlas_t1mni

    @gen_utils.timer
    def tissue2dwi_align(self):
        """alignment of ventricle and CC ROI's from MNI space --> dwi and CC and CSF from T1w space --> dwi
        A function to generate and perform dwi space alignment of avoidance/waypoint masks for tractography.
        First creates ventricle and CC ROI. Then creates transforms from stock MNI template to dwi space.
        NOTE: for this to work, must first have called both t1w2dwi_align and atlas2t1w2dwi_align.
        Raises
        ------
        ValueError
            Raised if FSL atlas for ventricle reference not found
        """

        # Create MNI-space ventricle mask
        print("Creating MNI-space ventricle ROI...")
        if not os.path.isfile(self.mni_atlas):
            raise ValueError("FSL atlas for ventricle reference not found!")
        cmd = f'fslmaths {self.mni_vent_loc} -thr 0.1 -bin {self.mni_vent_loc}'
        os.system(cmd)

        cmd = f'fslmaths {self.corpuscallosum} -bin {self.corpuscallosum}'
        os.system(cmd)

        cmd = f'fslmaths {self.corpuscallosum} -sub {self.mni_vent_loc} -bin {self.corpuscallosum}'
        os.system(cmd)

        # Create a transform from the atlas onto T1w. This will be used to transform the ventricles to dwi space.
        reg_utils.align(
            self.mni_atlas,
            self.input_mni,
            xfm=self.xfm_roi2mni_init,
            init=None,
            bins=None,
            dof=6,
            cost="mutualinfo",
            searchrad=True,
            interp="spline",
            out=None,
        )

        # Create transform to align roi to mni and T1w using flirt
        reg_utils.applyxfm(
            self.input_mni, self.mni_vent_loc, self.xfm_roi2mni_init, self.vent_mask_mni
        )

        if self.simple is False:
            # Apply warp resulting from the inverse MNI->T1w created earlier
            reg_utils.apply_warp(
                self.t1w_brain,
                self.vent_mask_mni,
                self.vent_mask_t1w,
                warp=self.mni2t1w_warp,
                interp="nn",
                sup=True,
            )

            # Apply warp resulting from the inverse MNI->T1w created earlier
            reg_utils.apply_warp(
                self.t1w_brain,
                self.corpuscallosum,
                self.corpuscallosum_mask_t1w,
                warp=self.mni2t1w_warp,
                interp="nn",
                sup=True,
            )

        # Applyxfm tissue maps to dwi space
        reg_utils.applyxfm(
            self.nodif_B0,
            self.vent_mask_t1w,
            self.t1wtissue2dwi_xfm,
            self.vent_mask_dwi,
        )
        qa_reg.reg_mri_pngs(self.vent_mask_dwi, self.nodif_B0, self.namer.dirs['qa']['reg'])
        reg_utils.applyxfm(
            self.nodif_B0,
            self.corpuscallosum_mask_t1w,
            self.t1wtissue2dwi_xfm,
            self.corpuscallosum_dwi,
        )
        qa_reg.reg_mri_pngs(self.corpuscallosum_dwi, self.nodif_B0, self.namer.dirs['qa']['reg'])
        reg_utils.applyxfm(
            self.nodif_B0, self.csf_mask, self.t1wtissue2dwi_xfm, self.csf_mask_dwi
        )
        qa_reg.reg_mri_pngs(self.csf_mask_dwi, self.nodif_B0, self.namer.dirs['qa']['reg'])
        reg_utils.applyxfm(
            self.nodif_B0, self.gm_mask, self.t1wtissue2dwi_xfm, self.gm_in_dwi
        )
        qa_reg.reg_mri_pngs(self.gm_in_dwi, self.nodif_B0, self.namer.dirs['qa']['reg'])
        reg_utils.applyxfm(
            self.nodif_B0, self.wm_mask, self.t1wtissue2dwi_xfm, self.wm_in_dwi
        )
        qa_reg.reg_mri_pngs(self.wm_in_dwi, self.nodif_B0, self.namer.dirs['qa']['reg'])

        # Threshold WM to binary in dwi space
        thr_img = nib.load(self.wm_in_dwi)
        thr_img.get_data()[thr_img.get_data() < 0.15] = 0
        nib.save(thr_img, self.wm_in_dwi_bin)

        # Threshold GM to binary in dwi space
        thr_img = nib.load(self.gm_in_dwi)
        thr_img.get_data()[thr_img.get_data() < 0.15] = 0
        nib.save(thr_img, self.gm_in_dwi_bin)

        # Threshold CSF to binary in dwi space
        thr_img = nib.load(self.csf_mask_dwi)
        thr_img.get_data()[thr_img.get_data() < 0.99] = 0
        nib.save(thr_img, self.csf_mask_dwi)

        # Threshold WM to binary in dwi space
        self.t_img = load_img(self.wm_in_dwi_bin)
        self.mask = math_img("img > 0", img=self.t_img)
        self.mask.to_filename(self.wm_in_dwi_bin)

        # Threshold GM to binary in dwi space
        self.t_img = load_img(self.gm_in_dwi_bin)
        self.mask = math_img("img > 0", img=self.t_img)
        self.mask.to_filename(self.gm_in_dwi_bin)

        # Threshold CSF to binary in dwi space
        self.t_img = load_img(self.csf_mask_dwi)
        self.mask = math_img("img > 0", img=self.t_img)
        self.mask.to_filename(self.csf_mask_dwi_bin)

        # Create ventricular CSF mask
        print("Creating ventricular CSF mask...")
        cmd = f'fslmaths {self.vent_mask_dwi} -kernel sphere 10 -ero -bin {self.vent_mask_dwi}'
        os.system(cmd)
        print("Creating Corpus Callosum mask...")
        cmd = f'fslmaths {self.corpuscallosum_dwi} -mas {self.wm_in_dwi_bin} -bin {self.corpuscallosum_dwi}'
        os.system(cmd)
        cmd = f'fslmaths {self.csf_mask_dwi} -add {self.vent_mask_dwi} -bin {self.vent_csf_in_dwi}'
        os.system(cmd)

        # Create gm-wm interface image
        cmd = (f'fslmaths {self.gm_in_dwi_bin} -mul {self.wm_in_dwi_bin} -add {self.corpuscallosum_dwi} '
            f'-sub {self.vent_csf_in_dwi} -mas {self.nodif_B0_mask} -bin {self.wm_gm_int_in_dwi}')
        os.system(cmd)



class DmriRegOld:
    def __init__(
        self, dwi, gtab, t1w, atlas, aligned_dwi, namer, clean=False, skull="none"
    ):
        """Aligns two images and stores the transform between them
        Parameters
        ----------
        dwi : str
            path to input image to be aligned as a nifti image file
        gtab : str
            path to file containing gradient driections and strength
        t1w : str
            path to reference image to be aligned to
        atlas : str
            path to roi atlas file
        aligned_dwi : str
            path for the output aligned dwi image
        namer : NameResource
            variable containing directory tree information for pipeline outputs
        clean : bool, optional
            Whether to delete intermediate files created by the pipeline, by default False
        skull : str, optional
            skullstrip parameter pre-set. Default is "none".
        """

        self.dwi = dwi
        self.t1w = t1w
        self.atlas = atlas
        self.gtab = gtab
        self.aligned_dwi = aligned_dwi
        self.namer = namer
        self.skull = skull

        # Creates names for all intermediate files used
        self.dwi_name = gen_utils.get_filename(dwi)
        self.t1w_name = gen_utils.get_filename(t1w)
        self.atlas_name = gen_utils.get_filename(atlas)

        self.temp_aligned = f'{self.namer.dirs["tmp"]["reg_a"]}/temp_aligned.nii.gz'
        self.temp_aligned2 = f'{self.namer.dirs["tmp"]["reg_a"]}/temp_aligned2.nii.gz'
        self.b0 = f'{self.namer.dirs["tmp"]["reg_a"]}/b0.nii.gz'
        self.t1w_brain = f'{self.namer.dirs["tmp"]["reg_a"]}/t1w_brain.nii.gz'
        self.xfm = f'{self.namer.dirs["tmp"]["reg_m"]}/{self.t1w_name}_{self.atlas_name}_xfm.mat'

    def dwi2atlas(self, clean=False):
        """Aligns the dwi image into atlas space
        Parameters
        ----------
        clean : bool, optional
            Whether to delete intermediate files created by this process, by default False
        """
        print("running dwi2atlas ...")
        # Loads DTI image in as data and extracts B0 volume
        self.dwi_im = nib.load(self.dwi)
        self.b0s = np.where(self.gtab.b0s_mask)[0]
        self.b0_im = np.squeeze(
            self.dwi_im.get_data()[:, :, :, self.b0s[0]]
        )  # if more than 1, use first

        # Wraps B0 volume in new nifti image
        self.b0_head = self.dwi_im.header
        self.b0_head.set_data_shape(self.b0_head.get_data_shape()[0:3])
        self.b0_out = nib.Nifti1Image(
            self.b0_im, affine=self.dwi_im.affine, header=self.b0_head
        )
        self.b0_out.update_header()
        nib.save(self.b0_out, self.b0)

        # Applies skull stripping to T1 volume, then EPI alignment to T1
        print(
            f'calling t1w_skullstrip on {self.t1w}, {self.t1w_brain}'
        )  # t1w = in, t1w_brain = out
        reg_utils.t1w_skullstrip(self.t1w, self.t1w_brain, self.skull)

        print(self.t1w)
        print(self.t1w_brain)
        print(self.temp_aligned)
        reg_utils.align_epi(self.dwi, self.t1w, self.t1w_brain, self.temp_aligned)

        # Applies linear registration from T1 to template
        print(
            f'calling reg_utils.align on {self.t1w}, {self.atlas}, {self.xfm}'
        )
        reg_utils.align(self.t1w, self.atlas, self.xfm)

        # Applies combined transform to dwi image volume
        print(
            f'calling reg_utils.applyxfm on {self.atlas}, {self.temp_aligned}, {self.xfm}, {self.temp_aligned2}'
        )
        reg_utils.applyxfm(self.atlas, self.temp_aligned, self.xfm, self.temp_aligned2)
        print(
            f'calling reg_utils.resample on {self.temp_aligned2}, {self.aligned_dwi}, {self.atlas}'
        )
        reg_utils.resample(self.temp_aligned2, self.aligned_dwi, self.atlas)

        if clean:
            cmd = f'rm -f {self.dwi} {self.temp_aligned} {self.b0} {self.xfm} {self.t1w_name}*'
            print("Cleaning temporary registration files...")
            os.system(cmd)