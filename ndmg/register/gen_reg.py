#!/usr/bin/env python -W ignore::DeprecationWarning

# Copyright 2019 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# register.py
# Repackaged for native space registrations by Derek Pisner on 2019-01-16
# Email: dpisner@utexas.edu.
# epi_register created by Eric Bridgeford.


import warnings

warnings.simplefilter("ignore")
import os
import nibabel as nib
import numpy as np
from nilearn.image import load_img, math_img
from ndmg.utils import gen_utils
from ndmg.utils import reg_utils


def direct_streamline_norm(streams, fa_path, namer):
    """Applys the Symmetric Diffeomorphic Registration (SyN) Algorithm onto the streamlines to the atlas space defined by .../atlases/reference_brains/FSL_HCP1065_FA_2mm.nii.gz
    
    Parameters
    ----------
    streams : str
        Path to streamlines.trk file to be transformed
    fa_path : str
        Path to subject's FA tensor image
    namer : name_resource
        variable containing all relevant pathing information
    
    Returns
    -------
    ArraySequence
        Transformed streamlines
    str
        Path to tractogram streamline file: streamlines_dsn.trk
    """
    import os.path as op
    from dipy.tracking.streamline import deform_streamlines
    from dipy.io.streamline import load_trk
    from ndmg.utils import reg_utils as regutils
    from dipy.tracking import utils

    if os.path.isdir("/ndmg_atlases"):
        # in docker
        atlas_dir = "/ndmg_atlases"
    else:
        # local
        atlas_dir = op.expanduser("~") + "/.ndmg/ndmg_atlases"

    template_path = atlas_dir + "/atlases/reference_brains/FSL_HCP1065_FA_2mm.nii.gz"

    streams_warp_png = namer.dirs["tmp"]["base"] + "/warp_qc.png"

    # Run SyN and normalize streamlines
    fa_img = nib.load(fa_path)
    vox_size = fa_img.get_header().get_zooms()[0]
    template_img = nib.load(template_path)
    template_data = template_img.get_data()

    # SyN FA->Template
    [mapping, affine_map] = regutils.wm_syn(
        template_path, fa_path, namer.dirs["tmp"]["base"]
    )
    [streamlines, _] = load_trk(streams, reference='same')

    # Warp streamlines
    adjusted_affine = affine_map.affine.copy()
    adjusted_affine[1][3] = -adjusted_affine[1][3]/vox_size**2
    mni_streamlines = deform_streamlines(streamlines, deform_field=mapping.get_forward_field()[-1:],
                                         stream_to_current_grid=template_img.affine,
                                         current_grid_to_world=adjusted_affine,
                                         stream_to_ref_grid=template_img.affine,
                                         ref_grid_to_world=np.eye(4))  # TODO : dipy 1.0.0

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


class DmriReg(object):
    """Class containing relevant paths and class methods for analysing tractography
    
    Parameters
    ----------
    namer : name_resource
        name_resource variable containing relevant directory tree information
    nodif_B0 : str
        path to mean b0 image
    nodif_B0_mask : str
        path to mean b0 mask (nodif_B0....nii.gz)
    t1w_in : str
        path to t1w file
    vox_size : str
        voxel resolution ('2mm' or '1mm')
    simple : bool
        Whether you want to attempt non-linear registration when transforming between mni, t1w, and dwi space
    
    Raises
    ------
    ValueError
        FSL atlas for ventricle reference not found
    """
    def __init__(self, namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size, simple):
        import os.path as op

        if os.path.isdir("/ndmg_atlases"):
            # in docker
            atlas_dir = "/ndmg_atlases"
        else:
            # local
            atlas_dir = op.expanduser("~") + "/.ndmg/ndmg_atlases"
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
        self.t12mni_xfm_init = "{}/xfm_t1w2mni_init.mat".format(
            self.namer.dirs["tmp"]["reg_m"]
        )
        self.mni2t1_xfm_init = "{}/xfm_mni2t1w_init.mat".format(
            self.namer.dirs["tmp"]["reg_m"]
        )
        self.t12mni_xfm = "{}/xfm_t1w2mni.mat".format(self.namer.dirs["tmp"]["reg_m"])
        self.mni2t1_xfm = "{}/xfm_mni2t1.mat".format(self.namer.dirs["tmp"]["reg_m"])
        self.mni2t1w_warp = "{}/mni2t1w_warp.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.warp_t1w2mni = "{}/warp_t12mni.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.t1w2dwi = "{}/{}_in_dwi.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.t1_aligned_mni = "{}/{}_aligned_mni.nii.gz".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.t1w_brain = "{}/{}_brain.nii.gz".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.dwi2t1w_xfm = "{}/dwi2t1w_xfm.mat".format(self.namer.dirs["tmp"]["reg_m"])
        self.t1w2dwi_xfm = "{}/t1w2dwi_xfm.mat".format(self.namer.dirs["tmp"]["reg_m"])
        self.t1w2dwi_bbr_xfm = "{}/t1w2dwi_bbr_xfm.mat".format(
            self.namer.dirs["tmp"]["reg_m"]
        )
        self.dwi2t1w_bbr_xfm = "{}/dwi2t1w_bbr_xfm.mat".format(
            self.namer.dirs["tmp"]["reg_m"]
        )
        self.t1wtissue2dwi_xfm = "{}/t1wtissue2dwi_xfm.mat".format(
            self.namer.dirs["tmp"]["reg_m"]
        )
        self.xfm_atlas2t1w_init = "{}/{}_xfm_atlas2t1w_init.mat".format(
            self.namer.dirs["tmp"]["reg_m"], self.t1w_name
        )
        self.xfm_atlas2t1w = "{}/{}_xfm_atlas2t1w.mat".format(
            self.namer.dirs["tmp"]["reg_m"], self.t1w_name
        )
        self.temp2dwi_xfm = "{}/{}_xfm_temp2dwi.mat".format(
            self.namer.dirs["tmp"]["reg_m"], self.dwi_name
        )

        self.input_mni = "%s%s%s%s" % (
            FSLDIR,
            "/data/standard/MNI152_T1_",
            vox_size,
            "_brain.nii.gz",
        )
        self.input_mni_mask = "%s%s%s%s" % (
            FSLDIR,
            "/data/standard/MNI152_T1_",
            vox_size,
            "_brain_mask.nii.gz",
        )
        self.temp2dwi_xfm = "{}/{}_xfm_temp2dwi.mat".format(
            self.namer.dirs["tmp"]["reg_m"], self.dwi_name
        )
        self.map_path = "{}/{}_seg".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.wm_mask = "{}/{}_wm.nii.gz".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.wm_mask_thr = "{}/{}_wm_thr.nii.gz".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.wm_edge = "{}/{}_wm_edge.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.t1w_name
        )
        self.csf_mask = "{}/{}_csf.nii.gz".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.gm_mask = "{}/{}_gm.nii.gz".format(
            self.namer.dirs["output"]["prep_anat"], self.t1w_name
        )
        self.xfm_roi2mni_init = "{}/roi_2_mni.mat".format(
            self.namer.dirs["tmp"]["reg_m"]
        )
        self.lvent_out_file = "{}/LVentricle.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.rvent_out_file = "{}/RVentricle.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.csf_mask_dwi = "{}/{}_csf_mask_dwi.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.gm_in_dwi = "{}/{}_gm_in_dwi.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.wm_in_dwi = "{}/{}_wm_in_dwi.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.csf_mask_dwi_bin = "{}/{}_csf_mask_dwi_bin.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.t1w_name
        )
        self.gm_in_dwi_bin = "{}/{}_gm_in_dwi_bin.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.t1w_name
        )
        self.wm_in_dwi_bin = "{}/{}_wm_in_dwi_bin.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.t1w_name
        )
        self.vent_mask_dwi = "{}/{}_vent_mask_dwi.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.t1w_name
        )
        self.vent_csf_in_dwi = "{}/{}_vent_csf_in_dwi.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.t1w_name
        )
        self.vent_mask_mni = "{}/vent_mask_mni.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.vent_mask_t1w = "{}/vent_mask_t1w.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.wm_gm_int_in_dwi = "{}/{}_wm_gm_int_in_dwi.nii.gz".format(
            namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.wm_gm_int_in_dwi_bin = "{}/{}_wm_gm_int_in_dwi_bin.nii.gz".format(
            namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.input_mni_sched = "%s%s" % (FSLDIR, "/etc/flirtsch/T1_2_MNI152_2mm.cnf")
        self.mni_atlas = "%s%s%s%s" % (
            FSLDIR,
            "/data/atlases/HarvardOxford/HarvardOxford-sub-prob-",
            vox_size,
            ".nii.gz",
        )
        self.mni_vent_loc = (
            atlas_dir
            + "/atlases/mask/HarvardOxford-thr25_space-MNI152NLin6_variant-lateral-ventricles_res-"
            + vox_dims
            + "_descr-brainmask.nii.gz"
        )
        self.corpuscallosum = (
            atlas_dir + "/atlases/mask/CorpusCallosum_res_" + vox_size + ".nii.gz"
        )
        self.corpuscallosum_mask_t1w = "{}/{}_corpuscallosum.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.t1w_name
        )
        self.corpuscallosum_dwi = "{}/{}_corpuscallosum_dwi.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.t1w_name
        )

    def gen_tissue(self):
        """Extracts the brain from the raw t1w image (as indicated by self.t1w), uses it to create WM, GM, and CSF masks,
        reslices all 4 files to the target voxel resolution and extracts the white matter edge. Each mask is saved to 
        location indicated by self.map_path
        """
        # BET needed for this, as afni 3dautomask only works on 4d volumes
        print("Extracting brain from raw T1w image...")
        reg_utils.t1w_skullstrip(self.t1w, self.t1w_brain)

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
        cmd = (
            "fslmaths "
            + self.wm_mask_thr
            + " -edge -bin -mas "
            + self.wm_mask_thr
            + " "
            + self.wm_edge
        )
        print("Extracting white matter edge ...")
        print(cmd)
        os.system(cmd)

        return

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
                reg_utils.inverse_warp(self.t1w_brain, self.mni2t1w_warp, self.warp_t1w2mni)

                # Get mat from MNI -> T1
                cmd = (
                    "convert_xfm -omat "
                    + self.mni2t1_xfm_init
                    + " -inverse "
                    + self.t12mni_xfm_init
                )
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
        cmd = "convert_xfm -omat " + self.dwi2t1w_xfm + " -inverse " + self.t1w2dwi_xfm
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
                cmd = (
                    "convert_xfm -omat "
                    + self.t1w2dwi_bbr_xfm
                    + " -inverse "
                    + self.dwi2t1w_bbr_xfm
                )
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

        return

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
        self.aligned_atlas_t1mni = "{}/{}_aligned_atlas_t1w_mni.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.atlas_name
        )
        self.aligned_atlas_skull = "{}/{}_aligned_atlas_skull.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"], self.atlas_name
        )
        self.dwi_aligned_atlas = "{}/{}_aligned_atlas.nii.gz".format(
            self.namer.dirs["output"]["reg_anat"], self.atlas_name
        )
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
            return self.aligned_atlas_t1mni

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
        cmd = "fslmaths " + self.mni_vent_loc + " -thr 0.1 -bin " + self.mni_vent_loc
        os.system(cmd)

        cmd = "fslmaths " + self.corpuscallosum + " -bin " + self.corpuscallosum
        os.system(cmd)

        cmd = (
            "fslmaths "
            + self.corpuscallosum
            + " -sub "
            + self.mni_vent_loc
            + " -bin "
            + self.corpuscallosum
        )
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
        reg_utils.applyxfm(
            self.nodif_B0,
            self.corpuscallosum_mask_t1w,
            self.t1wtissue2dwi_xfm,
            self.corpuscallosum_dwi,
        )
        reg_utils.applyxfm(
            self.nodif_B0, self.csf_mask, self.t1wtissue2dwi_xfm, self.csf_mask_dwi
        )
        reg_utils.applyxfm(
            self.nodif_B0, self.gm_mask, self.t1wtissue2dwi_xfm, self.gm_in_dwi
        )
        reg_utils.applyxfm(
            self.nodif_B0, self.wm_mask, self.t1wtissue2dwi_xfm, self.wm_in_dwi
        )

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
        cmd = (
            "fslmaths "
            + self.vent_mask_dwi
            + " -kernel sphere 10 -ero -bin "
            + self.vent_mask_dwi
        )
        os.system(cmd)
        print("Creating Corpus Callosum mask...")
        cmd = (
            "fslmaths "
            + self.corpuscallosum_dwi
            + " -mas "
            + self.wm_in_dwi_bin
            + " -bin "
            + self.corpuscallosum_dwi
        )
        os.system(cmd)
        cmd = (
            "fslmaths "
            + self.csf_mask_dwi
            + " -add "
            + self.vent_mask_dwi
            + " -bin "
            + self.vent_csf_in_dwi
        )
        os.system(cmd)

        # Create gm-wm interface image
        cmd = (
            "fslmaths "
            + self.gm_in_dwi_bin
            + " -mul "
            + self.wm_in_dwi_bin
            + " -add "
            + self.corpuscallosum_dwi
            + " -sub "
            + self.vent_csf_in_dwi
            + " -mas "
            + self.nodif_B0_mask
            + " -bin "
            + self.wm_gm_int_in_dwi
        )
        os.system(cmd)

        return


class dmri_reg_old(object):
    def __init__(self, dwi, gtab, t1w, atlas, aligned_dwi, namer, clean=False):
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
        namer : name_resource
            variable containing directory tree information for pipeline outputs
        clean : bool, optional
            Whether to delete intermediate files created by the pipeline, by default False
        """
        
        self.dwi = dwi
        self.t1w = t1w
        self.atlas = atlas
        self.gtab = gtab
        self.aligned_dwi = aligned_dwi
        self.namer = namer

        # Creates names for all intermediate files used
        self.dwi_name = gen_utils.get_filename(dwi)
        self.t1w_name = gen_utils.get_filename(t1w)
        self.atlas_name = gen_utils.get_filename(atlas)

        self.temp_aligned = "{}/temp_aligned.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.temp_aligned2 = "{}/temp_aligned2.nii.gz".format(
            self.namer.dirs["tmp"]["reg_a"]
        )
        self.b0 = "{}/b0.nii.gz".format(self.namer.dirs["tmp"]["reg_a"])
        self.t1w_brain = "{}/t1w_brain.nii.gz".format(self.namer.dirs["tmp"]["reg_a"])
        self.xfm = "{}/{}_{}_xfm.mat".format(
            self.namer.dirs["tmp"]["reg_m"], self.t1w_name, self.atlas_name
        )

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
            "calling t1w_skullstrip on {}, {}".format(self.t1w, self.t1w_brain)
        )  # t1w = in, t1w_brain = out
        reg_utils.t1w_skullstrip(self.t1w, self.t1w_brain)

        print("calling align_epi")
        print(self.t1w)
        print(self.t1w_brain)
        print(self.temp_aligned)
        reg_utils.align_epi(self.dwi, self.t1w, self.t1w_brain, self.temp_aligned)

        # Applies linear registration from T1 to template
        print("calling reg_utils.align on {}, {}, {}".format(self.t1w, self.atlas, self.xfm))
        reg_utils.align(self.t1w, self.atlas, self.xfm)

        # Applies combined transform to dwi image volume
        print(
            "calling reg_utils.applyxfm on {}, {}, {}, {}".format(
                self.atlas, self.temp_aligned, self.xfm, self.temp_aligned2
            )
        )
        reg_utils.applyxfm(self.atlas, self.temp_aligned, self.xfm, self.temp_aligned2)
        print(
            "calling reg_utils.resample on {}, {}, {}".format(
                self.temp_aligned2, self.aligned_dwi, self.atlas
            )
        )
        reg_utils.resample(self.temp_aligned2, self.aligned_dwi, self.atlas)

        if clean:
            cmd = "rm -f {} {} {} {} {}*".format(
                self.dwi, self.temp_aligned, self.b0, self.xfm, self.t1w_name
            )
            print("Cleaning temporary registration files...")
            os.system(cmd)
