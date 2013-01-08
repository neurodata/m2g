#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to Create a ZIP file on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory.
"""

import os
import tempfile, zipfile
import argparse

def zipFilesFromFolders(dirName = None, multiTuple = []):
    '''
    @deprecated
    @param dirName: any folder
    '''
    temp = tempfile.TemporaryFile()
    myzip = zipfile.ZipFile(temp ,'w', zipfile.ZIP_DEFLATED)

    if (multiTuple):
        for dirName in multiTuple:
            if dirName[0] != '.': # ignore metadata
                dirName = os.path.join(multiTuple, dirName)
                filesInOutputDir = os.listdir(dirName)

                for thefolder in filesInOutputDir:
                    if thefolder[0] != '.': # ignore metadata
                        dataProdDir = os.path.join(dirName, thefolder)
                        for thefile in os.listdir(dataProdDir):
                            filename =  os.path.join(dataProdDir, thefile)
                            myzip.write(filename, thefile) # second param of write determines name output
                            print "Compressing: " + thefile
        myzip.close()
        return temp


    filesInOutputDir = os.listdir(dirName)

    for thefolder in filesInOutputDir:
        if thefolder[0] != '.': # ignore metadata
            dataProdDir = os.path.join(dirName, thefolder)
            for thefile in os.listdir(dataProdDir):
                filename =  os.path.join(dataProdDir, thefile)
                myzip.write(filename, thefile) # second param of write determines name output
                print "Compressing: " + thefile

    myzip.close()
    return temp

def zipper(dir, zip_file):
    '''
    Write a zipfile from a directory

    @param dir: the path to directory to be zipped
    @type dir: string

    @param zip_file: name of zip file
    @type zip_file: string
    '''
    zip_file = tempfile.TemporaryFile()

    zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(dir))
    for root, dirs, files in os.walk(dir):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            print "Compressing: " + f
            zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
    zip.close()
    return zip_file

def unzip(zfilename, saveToDir ):
    '''
    Unzip a zipped folder

    @param zfilename: full filename of the zipfile
    @type zfilename: string

    @param saveToDir: the save location
    @type saveToDir: string
    '''

    # open the zipped file
    zfile = zipfile.ZipFile( zfilename, "r" )

    unzippedFiles = []

    # get each archived file and process the decompressed data
    for info in zfile.infolist():
        fname = info.filename
        # decompress each file's data
        data = zfile.read(fname)

        # save the decompressed data to a new file
        filename = os.path.join(saveToDir, fname)
        unzippedFiles.append(filename)
        fout = open(filename, "w")
        fout.write(data)
        fout.close()
        print "New file created --> %s" % filename

    return unzippedFiles

if __name__ == '__main__':
    main()

def main():

    parser = argparse.ArgumentParser(description='Zip the contents of an entire directory & place contents in single zip File')
    parser.add_argument('dirName', action='store')
    parser.add_argument('--multiTuple', action='store')

    result = parser.parse_args()

    zipFilesFromFolders(result.dirName, result.multiTuple)

if __name__ == '__main__':
    main()