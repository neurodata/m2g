import os
import tempfile, zipfile
import argparse

'''
Create a ZIP file on disk and transmit it in chunks of 8KB,                 
    without loading the whole file into memory.                            
'''
def zipFilesFromFolders(dirName, zipOutName):
    '''
    dirName - any folder
    zipOutName - the name of 
    '''

    temp = tempfile.TemporaryFile()
    filesInOutputDir = os.listdir(dirName)
    
    myzip = zipfile.ZipFile(temp ,'w', zipfile.ZIP_DEFLATED)
    
    for thefolder in filesInOutputDir:
        if thefolder[0] != '.': # ignore metadata
            dataProdDir = os.path.join(dirName, thefolder)
            for thefile in os.listdir(dataProdDir):
                filename =  os.path.join(dataProdDir, thefile)
                myzip.write(filename, thefile) # second param of write determines name output
                print "Compressing: " + thefile
    myzip.close()

    return temp

def main():
    
    parser = argparse.ArgumentParser(description='Zip the contents of an entire directory & place contents in single zip File')
    parser.add_argument('dirName', action="store")
    parser.add_argument('zipOutName', action="store")
    
    result = parser.parse_args()
    
    zipFilesFromFolders(result.dirName, result.zipOutName)
    
if __name__ == '__main__':
    main()