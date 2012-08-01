import os
import argparse

'''
Module creates a directory structure as defined by a string userDefProjectDir & moves files in
tuple args to the userDefProjectDir
'''
def createDirStruct(resultDirs):
    '''
    resultDirs - Directories to hold results
    
    '''
    
    for folder in resultDirs: 
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            print "%s, already exist" % folder
    
def main():
    
    parser = argparse.ArgumentParser(description='Create appropriate dir structure for a project')
    parser.add_argument('resultDir', action="store")
    
    result = parser.parse_args()
    
    createDirStruct(result.resultDir)
    
if __name__ == '__main__':
    main()