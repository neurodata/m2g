#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to create the directories necessary for the OCPIPELINE
"""

import os
import argparse
from shutil import move # For moving files

def create_dir_struct(resultDirs, derivFiles = None):
    '''
    @param resultDirs: Directories to hold results
    @type resultDirs: string

    @param derivFiles: The name of the derivatives files uploaded
    @type derivFiles: string
    '''

    newDir = ''
    if (derivFiles):
        for folder in resultDirs.split('/'):
            if (folder != ''):
                newDir += '/' + folder
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                else:
                    print "%s, already exists" % newDir

        for subfolder in ['derivatives/', 'rawdata/', 'graphs/', 'graphInvariants/']:
            if not os.path.exists(os.path.join(newDir, subfolder)):
                os.makedirs (os.path.join(newDir, subfolder))
            else:
                print "%s, already exists" % os.path.join(newDir, subfolder)

        ''' Move files into a derivative folder'''
        #### If duplicate proj,subj,session,site & scanID given - no duplicates for now #####
        for f in derivFiles:
            if not os.path.exists(os.path.join(resultDirs,'derivatives', f.split('/')[-1])):
                move(f, os.path.join(resultDirs, 'derivatives'))
            #else:
            #    print "%s, already in derivatives folder" % os.path.join(resultDirs,'derivatives', f.split('/')[-1])

            # Unqulify file names for processing
            if (f[-4:] == '.dat'):
                fiber_fn = f.split('/')[-1]
                #new_fiber_fn = os.path.join(resultDirs,'derivatives', f.split('/')[-1])
            elif (f[-4:] == '.xml'):
                roi_xml_fn = f.split('/')[-1]
                #new_roi_xml_fn = os.path.join(resultDirs,'derivatives', f.split('/')[-1])
            elif (f[-4:] == '.raw'):
                roi_raw_fn = f.split('/')[-1]
                #new_roi_raw_fn = os.path.join(resultDirs,'derivatives', f.split('/')[-1])

        return [fiber_fn, roi_xml_fn, roi_raw_fn]

    for folder in resultDirs:
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            print "%s, already exist" % folder

def main():
    parser = argparse.ArgumentParser(description='Create appropriate dir structure for a project')
    parser.add_argument('resultDir', action="store")
    parser.add_argument('derivFiles', action="store", default = None)


    result = parser.parse_args()

    create_dir_struct(result.resultDir, result.derivFiles)

if __name__ == '__main__':
    main()
