#!/usr/bin/env python

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

# bids_utils.py
# Created by Eric Bridgeford on 2017-08-09.
# Email: ebridge2@jhu.edu
import re
import os
from itertools import product

import boto3
from bids import BIDSLayout

from . import gen_utils as mgu


class NameResource:
    """
    A class for naming derivatives under the BIDs spec.
    """

    def __init__(self, modf, t1wf, tempf, opath):
        self.__subi__ = os.path.basename(modf).split(".")[0]
        self.__anati__ = os.path.basename(t1wf).split(".")[0]
        self.__sub__ = re.search(r"(sub-)(?!.*sub-).*?(?=[_])", modf).group()
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

    def add_dirs(self, paths, labels, label_dirs):
        """
        creates tmp and permanent directories for the desired suffixes.

        **Positional Arguments:
            - paths:
                - a dictionary of keys to suffix directories desired.
        """
        self.dirs = {}
        if not isinstance(labels, list):
            labels = [labels]
        dirtypes = ["output", "tmp", "qa"]
        for dirt in dirtypes:
            olist = [self.get_outdir()]
            self.dirs[dirt] = {}
            if dirt in ["tmp", "qa"]:
                olist = olist + [dirt] + self.get_sub_info()
            self.dirs[dirt]["base"] = os.path.join(*olist)
            for kwd, path in paths.iteritems():
                newdir = os.path.join(*[self.dirs[dirt]["base"], path])
                if kwd in label_dirs:  # levels with label granularity
                    self.dirs[dirt][kwd] = {}
                    for label in labels:
                        labname = self.get_label(label)
                        self.dirs[dirt][kwd][labname] = os.path.join(newdir, labname)
                else:
                    self.dirs[dirt][kwd] = newdir
        newdirs = flatten(self.dirs, [])
        cmd = "mkdir -p {}".format(" ".join(newdirs))
        mgu.execute_cmd(cmd)  # make the directories
        return

    def _get_outdir(self):
        """
        Called by constructor to initialize the output directory.
        """
        olist = [self.__basepath__]
        # olist.append(self.__sub__)
        # if self.__ses__:
        #    olist.append(self.__ses__)
        return os.path.join(*olist)

    def get_outdir(self):
        """
        Returns the base  output directory for a particular subject
        (+ appropriate granularity).
        """
        return self.__outdir__

    def get_template_info(self):
        """
        returns the formatted spatial information associated with a template.-
        """
        return "space-{}_{}".format(self.__space__, self.__res__)

    def get_template_space(self):
        return "space-{}_{}".format(self.__space__, self.__res__)

    def get_label(self, label):
        """
        return the formatted label information for the parcellation.
        """
        return mgu.get_filename(label)
        # return "label-{}".format(re.split(r'[._]',
        #                         os.path.basename(label))[0])

    def name_derivative(self, folder, derivative):
        """
        names a particular derivative by the following spec:

        self.__opath__/mod/type/[specific/]derivative

        ***Positional Arguments:**

            derivative:
                - the name of the file to be produced.
            mod:
                - the modality. Should be a BIDs-compliant name (bold, t1w,
                anat).
            type:
                - the inner directory to place the file.
            specific:
                - an additional, optional layer of granularity.
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
    if isinstance(current, dict):
        for key in current:
            flatten(current[key], result)
    else:
        result.append(current)
    return result


def sweep_directory(bdir, subj=None, sesh=None, task=None, run=None, modality="dwi"):
    """
    Given a BIDs formatted directory, crawls the BIDs dir and prepares the
    necessary inputs for the NDMG pipeline. Uses regexes to check matches for
    BIDs compliance.
    """
    if modality == "dwi":
        dwis = []
        bvals = []
        bvecs = []
    elif modality == "func":
        funcs = []
    anats = []
    layout = BIDSLayout(bdir)  # initialize BIDs tree on bdir
    # get all files matching the specific modality we are using
    if subj is None:
        subjs = layout.get_subjects()  # list of all the subjects
    else:
        subjs = as_list(subj)  # make it a list so we can iterate
    for sub in subjs:
        if not sesh:
            seshs = layout.get_sessions(subject=sub)
            seshs += [None]  # in case there are non-session level inputs
        else:
            seshs = as_list(sesh)  # make a list so we can iterate

        if not task:
            tasks = layout.get_tasks(subject=sub)
            tasks += [None]
        else:
            tasks = as_list(task)

        if not run:
            runs = layout.get_runs(subject=sub)
            runs += [None]
        else:
            runs = as_list(run)

        # all the combinations of sessions and tasks that are possible
        for (ses, tas, ru) in product(seshs, tasks, runs):
            # the attributes for our modality img
            mod_attributes = [sub, ses, tas, ru]
            # the keys for our modality img
            mod_keys = ["subject", "session", "task", "run"]
            # our query we will use for each modality img
            mod_query = {"modality": modality}
            if modality == "dwi":
                type_img = "dwi"  # use the dwi image
            elif modality == "func":
                type_img = "bold"  # use the bold image
            mod_query["type"] = type_img

            for attr, key in zip(mod_attributes, mod_keys):
                if attr:
                    mod_query[key] = attr

            anat_attributes = [sub, ses]  # the attributes for our anat img
            anat_keys = ["subject", "session"]  # the keys for our modality img
            # our query for the anatomical image
            anat_query = {"modality": "anat", "type": "T1w", "extensions": "nii.gz|nii"}
            for attr, key in zip(anat_attributes, anat_keys):
                if attr:
                    anat_query[key] = attr
            # make a query to fine the desired files from the BIDSLayout
            anat = layout.get(**anat_query)
            if modality == "dwi":
                dwi = layout.get(**merge_dicts(mod_query, {"extensions": "nii.gz|nii"}))
                bval = layout.get(**merge_dicts(mod_query, {"extensions": "bval"}))
                bvec = layout.get(**merge_dicts(mod_query, {"extensions": "bvec"}))
                if anat and dwi and bval and bvec:
                    for (dw, bva, bve) in zip(dwi, bval, bvec):
                        if dw.filename not in dwis:
                            # if all the required files exist, append by the first
                            # match (0 index)
                            anats.append(anat[0].filename)
                            dwis.append(dw.filename)
                            bvals.append(bva.filename)
                            bvecs.append(bve.filename)
            elif modality == "func":
                func = layout.get(
                    **merge_dicts(mod_query, {"extensions": "nii.gz|nii"})
                )
                if func and anat:
                    for fun in func:
                        if fun.filename not in funcs:
                            funcs.append(fun.filename)
                            anats.append(anat[0].filename)
    if modality == "dwi":
        if not len(dwis) or not len(bvals) or not len(bvecs) or not len(anats):
            print("No dMRI files found in BIDs spec. Skipping...")
        return (dwis, bvals, bvecs, anats)
    elif modality == "func":
        if not len(funcs) or not len(anats):
            print("No fMRI files found in BIDs spec. Skipping...")
        return (funcs, anats)
    else:
        raise ValueError(
            "Incorrect modality passed.\
                         Choices are 'func' and 'dwi'."
        )


def as_list(x):
    """
    A function to convert an item to a list if it is not, or pass
    it through otherwise.
    """
    if not isinstance(x, list):
        return [x]
    else:
        return x


def merge_dicts(x, y):
    """
    A function to merge two dictionaries, making it easier for us to make
    modality specific queries for dwi images (since they have variable
    extensions due to having an nii.gz, bval, and bvec file).
    """
    z = x.copy()
    z.update(y)
    return z
