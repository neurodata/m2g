'''
This is just for Disa to do random testing
LCC & testing
'''

lccOutputFileName = "/Users/dmhembere44/Desktop/LCC.npy" # output of LCC
embedSVDOutputFileName = "/Users/dmhembere44/Desktop/Embed.npy"
inputRoi_raw = "/data/MR.new/roi/M87102217_roi.raw"
inputRoi_xml = "/data/MR.new/roi/M87102217_roi.xml"
inputFiber_dat = "/data/MR.new/fiber/M87102217_fiber.dat"
bigGraphOutputFileName = "/Users/dmhembere44/Downloads/projectStampThu05Jul2012_11.35.16_/SmallGraph.mat"    

from mrcap import lcc as lcc
from mrcap import Embed as Embed
from mrcap import gengraph as gengraph

def processLCC():
    global lccOutputFileName
    
    global inputRoi_raw
    global inputRoi_xml
    global inputFiber_dat
    
    global bigGraphOutputFileName
    
    lcc.process_single_brain(inputRoi_xml, inputRoi_raw, bigGraphOutputFileName, lccOutputFileName)

import numpy as np

def embed_graph(ccfn, roiRootName, fgfn, embedfn, dim=10):
    """
    ccfn - connected components file with numpy arrray
    roiRootName - roi files root name
    fgfn - mat file with the fibergraph
    embedfn - full file name of output file to be saved
    dim - desired dimension for the embedding
    """
    
    vcc = lcc.ConnectedComponent(fn =ccfn)
    # Load the fibergraph
    fg = lcc._load_fibergraph(roiRootName, fgfn) 
    
    # Now get the subgraph for the lcc, binarize and symmetrize
    G = vcc.induced_subgraph(fg.spcscmat)
    G.data = np.ones_like(G.data) # Binarize
    G = G+G.T # Symmetrize

    e = Embed.Embed(dim, matrix=Embed.self_matrix)
    np.save(embedfn, e.embed(G).get_scaled())

def rungenGraph():
    
    global inputRoi_raw
    global inputRoi_xml
    global inputFiber_dat
    
    out = "/Users/dmhembere44/Desktop/genGraphOut.mat"
    gengraph.genGraph(inputFiber_dat, out)

def main():
    #rungenGraph();
    #processLCC();
    
    global bigGraphOutputFileName
    global lccOutputFileName
    global inputRoi_raw
    global inputRoi_xml
    global inputFiber_dat
    global embedSVDOutputFileName
    
    embed_graph(lccOutputFileName, inputRoi_xml[:-4] , bigGraphOutputFileName, embedSVDOutputFileName);
    
if __name__ == '__main__':  
    short = inputRoi_xml[:-4]
    print type(short)
    print inputRoi_xml[:-4]
    


'''
def multByTwo(one, two = 0, three = 0):
    if not (two and three):
        print one*10
    else:
        print one*two*three
    
def main():
    multByTwo(1,2,3);
    
if __name__ == '__main__':
    main()
'''




























#import os

# Path stuff
'''
currDirPath = os.path.abspath(os.path.dirname(__file__))
outputDir = 'OUTPUTFolder'
outputDirPath = os.path.join(currDirPath, outputDir )
listing = os.listdir(outputDirPath)

print outputDirPath + "/"+ listing[0]
print listing
'''

'''
uploadDirPath = os.path.abspath(os.pardir) + "/media/documents" # Global upload path
downloadDirPath = os.path.abspath(os.pardir) + "/media/outputDocuments" # Global path

def trial():
    
    global uploadDirPath
    filesInUploadDir = os.listdir(uploadDirPath) # WHE DA PROBLEM AT
    print uploadDirPath
    print filesInUploadDir

def main():
    trial()
    
if __name__ == '__main__':
    main()
'''
'''
for i in range(500000):
    print "I AM IN trial.py", i
'''
#from sys import argv
#fileName = argv;
#fileName[0]

