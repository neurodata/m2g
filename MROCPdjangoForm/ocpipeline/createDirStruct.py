import os
import argparse
from shutil import move, rmtree # For moving files

'''
Module creates a directory structure as defined by a string userDefProjectDir & moves files in
tuple args to the userDefProjectDir
'''
def createDirStruct(userDefProjectDir, uploadDirPath, endingDir, tempDirPath, moveFileNames):
    '''
    userDefProjectDir - the user defined project directory structure
    uploadDirPath - the location of the files to be placed in userDefProjectDir
    moveFileNames - tuple of file names in temporary location uploadDirPath
    tempDirPath - temp directory holding files we are concerned with
    projectName - the temp project name different from user def project name
    endingDir - is the directory where the files in the temp location should be moved to
    '''
    
    dataProds = ['derivatives/', 'rawdata/', 'graphs/', 'graphInvariants/']
    
    for folder in dataProds: 
        if not os.path.exists(userDefProjectDir + folder):
            os.makedirs(userDefProjectDir + folder)
        else:
            print "Folder does exist!"
    
    ''' Move files to appropriate location '''            
    uploadedFiles = [ os.path.join(uploadDirPath, moveFileNames[0]), os.path.join(uploadDirPath, moveFileNames[1])
                     ,os.path.join(uploadDirPath, moveFileNames[2]) ]
    
    i = 0
    for thefile in uploadedFiles:
        if not os.path.exists(os.path.join(endingDir,moveFileNames[i])): # If its already there... leave it alone & use the old one
            move(thefile, endingDir) # Where to save derivatives
        else:
            print 'File does exist!'
        i += 1
        
    
    ''' Delete project in temp folder'''
    rmtree(uploadDirPath)
    
def main():
    
    parser = argparse.ArgumentParser(description='Create appropriate dir structure for project & move files that are in temp folder')
    parser.add_argument('userDefProjectDir', action="store")
    parser.add_argument('uploadDirPath', action="store")
    parser.add_argument('endingDir', action="store")
    parser.add_argument('tempDirPath', action="store")
    parser.add_argument('moveFileNames', action="store")
    
    result = parser.parse_args()
    
    createDirStruct(result.dirName, result.zipOutName)
    
if __name__ == '__main__':
    main()