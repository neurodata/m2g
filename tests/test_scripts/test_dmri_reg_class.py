import ndmg
from ndmg import preproc as mgp
from ndmg.utils import gen_utils as mgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock, MagicMock	
import nibabel as nib
import numpy as np 
import pytest
import os



namer = MagicMock()
namer.dirs = {'tmp': {'reg_m': 'r', 'reg_a': 'r'}, 'output': {'reg_anat': 'ab'}}

def test_dmri_reg_init():
	nodif_B0 = 
	nodif_B0_mask = 
	t1w = 
	vox_size = 
	
	#instantiate object
	reg = mgr.dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w, vox_size, simple=False)

	#check attributes:
	assert  reg.simple == simple
    assert  reg.nodif_B0 = nodif_B0
    assert  reg.nodif_B0_mask = nodif_B0_mask
    assert  reg.t1w = t1w_in
    assert  reg.vox_size = vox_size
    assert  reg.t1w_name = "t1w"
    assert  reg.dwi_name = "dwi"
    assert  self.namer = namer
    assert  self.t12mni_xfm_init = "{}/xfm_t1w2mni_init.mat".format( self.namer.dirs["tmp"]["reg_m"]
        )
    assert    self.mni2t1_xfm_init = "{}/xfm_mni2t1w_init.mat".format(self.namer.dirs["tmp"]["reg_m"]
        )
    assert   self.t12mni_xfm = "{}/xfm_t1w2mni.mat".format(self.namer.dirs["tmp"]["reg_m"])
    assert    self.mni2t1_xfm = "{}/xfm_mni2t1.mat".format(self.namer.dirs["tmp"]["reg_m"])
    assert    self.mni2t1w_warp = "{}/mni2t1w_warp.nii.gz".format(  self.namer.dirs["tmp"]["reg_a"])
    assert    self.warp_t1w2mni = "{}/warp_t12mni.nii.gz".format(
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