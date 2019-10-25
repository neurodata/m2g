# Copyright 2016 NeuroData (http://neurodata.io)
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

# qa_mri.py
# Created by Eric W Bridgeford on 2016-06-08.
# Email: ebridge2@jhu.edu

import warnings

warnings.simplefilter("ignore")
import nibabel as nb
import sys
import re
import os.path
import matplotlib
import numpy as np
from ndmg.utils import gen_utils as mgu

# from ndmg.stats.func_qa_utils import plot_timeseries, plot_signals, \
#    registration_score, plot_connectome
# from ndmg.stats.qa_reg import reg_mri_pngs, plot_brain, plot_overlays
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv


class qa_mri(object):
    def __init__(self, name, modality):
        self.namer = name
        self.modality = modality
        pass

    def load(self, filename):
        """
        A function for loading a qa_mri object, so that we
        can perform group level quality control easily.

        **Positional Arguments:**

            filename: the name of the pickle file containing
                our qa_func object
        """
        reader = csv.reader(filename, delimiter=":")
        self.__dict__ = dict(reader)
        return self

    def save(self, filename, exetime):
        """
        A function for saving a qa_mri object.

        **Positional Arguments:**

            filename:
                - the name of the file we want to save to.
            exetime:
                - the runtime in seconds.
        """
        self.runtime = exetime
        attributes = [a for a in dir(self) if not a.startswith("__")]
        with open(filename, "w") as file:
            wr = csv.writer(file, delimiter=":")
            for key, value in list(self.__dict__.items()):
                wr.writerow([key, value])
        pass

    def func_preproc_qa(self, prep):
        """
        A function for performing quality control given motion
        correction information. Produces plots of the motion correction
        parameters used.

        **Positional Arguments**

            prep:
                - the module used for preprocessing.
            scan_id:
                - the id of the subject.
        """
        print("Performing QA for Functional Preprocessing...")
        func_name = mgu.get_filename(prep.preproc_func)

        raw_im = nb.load(prep.func)
        raw_dat = raw_im.get_data()

        # plot the uncorrected brain. this brain, if motion
        # is significant, will show a poorly defined border
        # since the brain will be moving in time
        rawfig = plot_brain(raw_dat.mean(axis=3), minthr=10)
        rawfig.savefig(
            "{}/{}_raw.png".format(self.namer.dirs["qa"]["prep_m"], func_name)
        )

        prep_im = nb.load(prep.preproc_func)
        prep_dat = prep_im.get_data()

        # plot the preprocessed brain. this brain should
        # look less blurred since the brain will be fixed in time
        # due to motion correction
        prepfig = plot_brain(prep_dat.mean(axis=3), minthr=10)
        nvols = prep_dat.shape[3]
        prepfig.savefig(
            "{}/{}_preproc.png".format(self.namer.dirs["qa"]["prep_m"], func_name)
        )

        # get the functional preprocessing motion parameters
        mc_params = np.genfromtxt(prep.mc_params)

        # Note that our translational parameters (first 3 columns of motion
        # params) are already in mm. For the rotational params, we use
        # Power et. al and assume brain rad of 500 mm, and given our radial
        # coords translate back to euclidian space so our displacement of
        # the x, y, z rotations is the displacement of the outer edge
        # of the brain
        mc_params[:, 0:3] = 500 * np.pi * mc_params[:, 0:3] / 180

        vd_pars = np.zeros(mc_params.shape)

        # our array of the displacements in x, y, z translations and rotations
        # volume wise displacement parameters for each x, y, z trans/rotation
        vd_pars[1:None, :] = mc_params[1:None, :] - mc_params[0:-1, :]

        # using the displacements, compute the euclidian distance of the
        # movement from volume to volume, given no displacement at the start
        fd_pars = np.linalg.norm(vd_pars, axis=1)
        # separate out the translational and rotational parameters, so we can
        # use them for statistics later
        trans_pars = np.split(mc_params[:, 3:6], 3, axis=1)
        rot_pars = np.split(mc_params[:, 0:3], 3, axis=1)
        # list of lists, where each list is the parameter
        # we will want a plot of
        # note that fd_pars is just an array, so we need to make
        # it a single-element list
        mc_pars = [trans_pars, rot_pars, [fd_pars]]

        # names to append to plots so they can be found easily
        mp_names = ["trans", "rot", "FD"]
        # titles for the plots
        mp_titles = [
            "Translational Parameters",
            "Rotational Parameters",
            "Framewise Displacement",
        ]
        # list of lists of the line labels
        linelegs = [
            ["x trans", "y trans", "z trans"],
            ["x rot", "y rot", "z rot"],
            ["framewise"],
        ]
        xlab = "Timepoint (TR)"
        ylab = "Displacement (mm)"
        # iterate over tuples of the lists we store our plot variables in
        for (param_type, name, title, legs) in zip(
            mc_pars, mp_names, mp_titles, linelegs
        ):
            params = []
            labels = []
            # iterate over the parameters while iterating over the legend
            # labels for each param
            params = [param for param in param_type]
            labels = [" {} displacement".format(leg) for leg in legs]
            fig = plot_signals(params, labels, title=title, xlabel=xlab, ylabel=ylab)

            fname_reg = "{}/{}_{}_parameters.png".format(
                self.namer.dirs["qa"]["prep_m"], func_name, name
            )
            fig.savefig(fname_reg, format="png")
            plt.close(fig)

        # framewise-displacement statistics
        prep.max_fd = np.max(fd_pars)
        prep.mean_fd = np.mean(fd_pars)
        prep.std_fd = np.std(fd_pars)
        # number of framewise displacements greater than .2 mm
        prep.num_fd_gt_200um = np.sum(fd_pars > 0.2)
        # number of framewise displacements greater than .5 mm
        prep.num_fd_gt_500um = np.sum(fd_pars > 0.5)
        pass

    def anat_preproc_qa(self, prep):
        """
        A function that produces anatomical preprocessing quality assurance
        figures.

        **Positional Arguments:**

            - prep:
                - the preprocessing object.
            - qa_dir:
                - the directory to place figures.
        """
        print("Performing QA for Anatoical Preprocessing...")
        figs = {}
        # produce plots for the raw anatomical image
        figs["raw_anat"] = plot_brain(prep.anat)
        # produce the preprocessed skullstripped anatomical image plot
        figs["preproc_brain"] = plot_overlays(prep.anat, prep.anat_preproc_brain)
        # save iterator
        for plotname, fig in figs.items():
            fname = "{}/{}_{}.png".format(
                self.namer.dirs["qa"]["prep_a"], prep.anat_name, plotname
            )
            fig.tight_layout()
            fig.savefig(fname)
            plt.close(fig)
        pass

    def self_reg_qa(self, reg):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**

            freg:
                - the func_register object from registration.
        """
        print("Performing QA for Self-Registration...")
        # overlap statistic for the functional and anatomical
        # skull-off brains
        (sreg_sc, sreg_fig) = registration_score(reg.sreg_brain, reg.t1w_brain)
        self.self_reg_sc = sreg_sc
        # use the jaccard score in the filepath to easily
        # identify failed subjects
        sreg_m_final = "{}/space-T1w/{}_jaccard_{:.0f}".format(
            self.namer.dirs["qa"]["reg_m"], reg.sreg_strat, self.self_reg_sc * 1000
        )
        sreg_a_final = "{}/space-T1w/{}_jaccard_{:.0f}".format(
            self.namer.dirs["qa"]["reg_a"], reg.sreg_strat, self.self_reg_sc * 1000
        )
        cmd = "mkdir -p {} {}".format(sreg_m_final, sreg_a_final)
        mgu.execute_cmd(cmd)
        sreg_fig.savefig(
            "{}/{}_bold_t1w_overlap.png".format(
                sreg_m_final, self.namer.get_mod_source()
            )
        )
        # produce plot of the white-matter mask used during bbr
        if mreg.wm_mask is not None:
            mask_dat = nb.load(reg.wm_mask).get_data()
            t1w_dat = nb.load(reg.t1w_brain).get_data()
            m_mask = plot_overlays(t1w_dat, mask_dat, minthr=0, maxthr=100)
            fname_mask = "{}/{}_{}.png".format(
                sreg_a_final, self.namer.get_anat_source(), "wmm"
            )
            m_mask.savefig(fname_mask, format="png")
            plt.close(m_mask)

        plt.close(sreg_fig)
        pass

    def aligned_mri_name(self):
        """
        A util to return aligned func name.
        """
        return "{}_{}".format(
            self.namer.get_mod_source(), self.namer.get_template_info()
        )

    def aligned_anat_name(self):
        """
        A util to return aligned func name.
        """
        return "{}_{}".format(
            self.namer.get_anat_source(), self.namer.get_template_info()
        )

    def temp_reg_qa(self, reg):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**

            freg:
                - the functional registration object.
        """
        print("Performing QA for Template-Registration...")
        # overlap statistic and plot btwn template-aligned fmri
        # and the atlas brain that we are aligning to
        (treg_sc, treg_fig) = registration_score(
            reg.taligned_epi, reg.atlas_brain, edge=True
        )
        # use the registration score in the filepath for easy
        # identification of failed subjects
        self.temp_reg_sc = treg_sc
        treg_m_final = "{}/template/{}_jaccard_{:.0f}".format(
            self.namer.dirs["qa"]["reg_m"], reg.treg_strat, self.temp_reg_sc * 1000
        )
        treg_a_final = "{}/template/{}_jaccard_{:.0f}".format(
            self.namer.dirs["qa"]["reg_a"], reg.treg_strat, self.temp_reg_sc * 1000
        )
        cmd = "mkdir -p {} {}".format(treg_m_final, treg_a_final)
        mgu.execute_cmd(cmd)
        mri_name = self.aligned_mri_name()
        treg_fig.savefig("{}/{}_epi2temp_overlap.png".format(treg_m_final, mri_name))
        plt.close(treg_fig)
        t1w_name = self.aligned_anat_name()
        # overlap between the template-aligned t1w and the atlas brain
        # that we are aligning to
        t1w2temp_fig = plot_overlays(
            reg.taligned_t1w, freg.atlas_brain, edge=True, minthr=0, maxthr=100
        )
        t1w2temp_fig.savefig("{}/{}_t1w2temp.png".format(treg_a_final, t1w_name))
        plt.close(t1w2temp_fig)
        # produce cnr, snr, and mean plots for temporal voxelwise statistics
        self.voxel_qa(reg.epi_aligned_skull, reg.atlas_mask, treg_m_final)
        pass

    def voxel_qa(self, func, mask, qadir):
        """
        A function to compute voxelwise statistics, such as voxelwise mean,
        voxelwise snr, voxelwise cnr, for an image, and produce related
        qa plots.

        **Positional Arguments:**

            func:
                - the path to the functional image we want statistics for.
            mask:
                - the path to the anatomical mask.
            qadir:
                - the directory to place qa images.
        """
        # estimating mean signal intensity and deviation in brain/non-brain
        fmri = nb.load(func)
        mask = nb.load(mask)
        fmri_dat = fmri.get_data()
        mask_dat = mask.get_data()

        # threshold to identify the brain and non-brain regions of the atlas
        brain = fmri_dat[mask_dat > 0, :]
        non_brain = fmri_dat[mask_dat == 0, :]
        # identify key statistics
        mean_brain = brain.mean()  # mean of each brain voxel (signal)
        std_nonbrain = np.nanstd(non_brain)  # std of nonbrain voxels (noise)
        std_brain = np.nanstd(brain)  # std of brain voxels (contrast)
        self.snr = mean_brain / std_nonbrain  # definition of snr
        self.cnr = std_brain / std_nonbrain  # definition of cnr

        func_name = self.aligned_mri_name()

        np.seterr(divide="ignore", invalid="ignore")
        mean_ts = fmri_dat.mean(axis=3)  # temporal mean
        snr_ts = np.divide(mean_ts, std_nonbrain)  # temporal snr
        # temporal cnr
        cnr_ts = np.divide(np.nanstd(fmri_dat, axis=3), std_nonbrain)

        plots = {}
        plots["mean"] = plot_brain(mean_ts, minthr=10)
        plots["snr"] = plot_brain(snr_ts, minthr=10)
        plots["cnr"] = plot_brain(cnr_ts, minthr=10)
        for plotname, plot in plots.items():
            fname = "{}/{}_{}.png".format(qadir, func_name, plotname)
            plot.savefig(fname, format="png")
            plt.close(plot)
        pass

    def nuisance_qa(self, nuisobj):
        """
        A function to assess the quality of nuisance correction.

        **Positional Arguments**

            nuisobj:
                - the nuisance correction object.
        """
        print("Performing QA for Nuisance...")
        qcadir = self.namer.dirs["qa"]["nuis_a"]
        qcfdir = self.namer.dirs["qa"]["nuis_f"]
        maskdir = "{}/{}".format(qcadir, "masks")
        glmdir = "{}/{}".format(qcfdir, "glm_correction")
        fftdir = "{}/{}".format(qcfdir, "filtering")

        cmd = "mkdir -p {} {} {}".format(maskdir, glmdir, fftdir)
        mgu.execute_cmd(cmd)

        anat_name = self.aligned_anat_name()
        t1w_dat = nb.load(nuisobj.smri).get_data()
        # list of all possible masks
        masks = [nuisobj.lv_mask, nuisobj.wm_mask, nuisobj.gm_mask, nuisobj.er_wm_mask]
        masknames = ["csf_mask", "wm_mask", "gm_mask", "eroded_wm_mask"]
        # iterate over masks for existence and plot overlay if they exist
        # since that means they were used at some point
        for mask, maskname in zip(masks, masknames):
            if mask is not None:
                mask_dat = nb.load(mask).get_data()
                # produce overlay figure between the t1w image that has
                # segmentation performed on it and the respective mask
                f_mask = plot_overlays(t1w_dat, mask_dat, minthr=0, maxthr=100)
                fname_mask = "{}/{}_{}.png".format(maskdir, anat_name, maskname)
                f_mask.savefig(fname_mask, format="png")
                plt.close(f_mask)

        # GLM regressors we could have
        glm_regs = [nuisobj.csf_reg, nuisobj.wm_reg, nuisobj.mot_reg, nuisobj.cc_reg]
        glm_names = ["csf", "wm", "friston", "compcor"]
        glm_titles = [
            "CSF Regressors",
            "White-Matter Regressors",
            "Motion Regressors",
            "aCompCor Regressors",
        ]
        # whether we should include legend labels
        label_include = [True, True, False, True]
        func_name = self.aligned_mri_name()
        # iterate over tuples of our plotting variables
        for (reg, name, title, lab) in zip(
            glm_regs, glm_names, glm_titles, label_include
        ):
            # if we have a particular regressor
            if reg is not None:
                regs = []
                labels = []
                nreg = reg.shape[1]  # number of regressors for a particular
                # nuisance variable
                # store each regressor as a element of our list
                regs = [reg[:, i] for i in range(0, nreg)]
                # store labels in case they are plotted
                labels = ["{} reg {}".format(name, i) for i in range(0, nreg)]
                # plot each regressor as a line
                fig = plot_signals(
                    regs,
                    labels,
                    title=title,
                    xlabel="Timepoint",
                    ylabel="Intensity",
                    lab_incl=lab,
                )
                fname_reg = "{}/{}_{}_regressors.png".format(glmdir, func_name, name)
                fig.savefig(fname_reg, format="png")
                plt.close(fig)
        # signal before compared with the signal removed and
        # signal after correction
        fig_glm_sig = plot_signals(
            [nuisobj.cent_nuis, nuisobj.glm_sig, nuisobj.glm_nuis],
            ["Before", "Regressed Sig", "After"],
            title="Impact of GLM Regression on Average GM Signal",
            xlabel="Timepoint",
            ylabel="Intensity",
        )
        fname_glm_sig = "{}/{}_glm_signal_cmp.png".format(glmdir, func_name)
        fig_glm_sig.savefig(fname_glm_sig, format="png")
        plt.close(fig_glm_sig)

        # Frequency Filtering
        if nuisobj.fft_reg is not None:
            cmd = "mkdir -p {}".format(fftdir)
            mgu.execute_cmd(cmd)
            # start by just plotting the average fft of gm voxels and
            # compare with average fft after frequency filtering
            fig_fft_pow = plot_signals(
                [nuisobj.fft_bef, nuisobj.fft_reg],
                ["Before", "After"],
                title="Average Gray Matter Power Spectrum",
                xlabel="Frequency",
                ylabel="Power",
                xax=nuisobj.freq_ra,
            )
            fname_fft_pow = "{}/{}_fft_power.png".format(fftdir, func_name)
            fig_fft_pow.savefig(fname_fft_pow, format="png")
            plt.close(fig_fft_pow)
            # plot the signal vs the regressed signal vs signal after
            fig_fft_sig = plot_signals(
                [nuisobj.glm_nuis, nuisobj.fft_sig, nuisobj.fft_nuis],
                ["Before", "Regressed Sig", "After"],
                title="Impact of Frequency Filtering on Average GM Signal",
                xlabel="Timepoint",
                ylabel="Intensity",
            )
            fname_fft_sig = "{}/{}_fft_signal_cmp.png".format(fftdir, func_name)
            fig_fft_sig.savefig(fname_fft_sig, format="png")
            plt.close(fig_fft_sig)
        pass

    def roi_graph_qa(self, timeseries, connectome, func, anat, label):
        """
        A function to perform ROI timeseries quality control.

        **Positional Arguments**

            timeseries:
                - a path to the ROI timeseries.
            func:
                - the functional image that has timeseries
                extract from it.
            anat:
                - the anatomical image that is aligned.
            label:
                - the label in which voxel timeseries will be
                downsampled.
            qcdir:
                - the quality control directory to place outputs.
        """
        label_name = self.namer.get_label(label)
        qcdir = self.namer.dirs["qa"]["conn"][label_name]
        print("Performing QA for ROI Analysis...")
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)

        # overlap between the temp-aligned t1w and the labelled parcellation
        reg_mri_pngs(anat, label, qcdir, minthr=10, maxthr=95)
        # overlap between the temp-aligned fmri and the labelled parcellation
        reg_mri_pngs(func, label, qcdir, minthr=10, maxthr=95)
        # plot the timeseries for each ROI and the connectivity matrix
        fname_ts = "{}/{}_{}_timeseries.html".format(
            qcdir, self.aligned_mri_name(), label_name
        )
        fname_con = "{}/{}_{}_measure-correlation.html".format(
            qcdir, self.aligned_mri_name(), label_name
        )
        if self.modality == "func":
            plot_timeseries(timeseries, fname_ts, self.aligned_mri_name(), label_name)
        plot_connectome(connectome, fname_con, self.aligned_mri_name(), label_name)
        pass

    def voxel_ts_qa(self, timeseries, voxel_func, atlas_mask):
        """
        A function to analyze the voxel timeseries extracted.

        **Positional Arguments**

            voxel_func:
                - the functional timeseries that
              has voxel timeseries extracted from it.
            atlas_mask:
                - the mask under which
              voxel timeseries was extracted.
            qcdir:
                - the directory to place qc in.
        """
        print("Performing QA for Voxel Timeseries...")
        qcdir = self.namer.dirs["qa"]["ts_voxel"]
        # plot the voxelwise signal with respect to the atlas to
        # get an idea of how well the fmri is masked
        reg_mri_pngs(voxel_func, atlas_mask, qcdir, loc=0, minthr=10, maxthr=95)
        pass
