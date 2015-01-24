#!/usr/local/bin/python2.7

import sys
from sys import argv
import numpy
from xml.dom import minidom
import os.path
import shutil

def main():
    params = list(argv)

    inputRawXML = params[1]
    outputDir = params[2]

    inputRawIMG = inputRawXML.split(".")[0] + ".raw"

    xmlFileName = os.path.basename(inputRawXML)
    
    outputRaw = xmlFileName.split(".")[0] + "_cp.raw"
    outputXml = xmlFileName.split(".")[0] + "_cp.xml"
    
    outputRaw = os.path.join(outputDir,outputRaw)
    outputXml = os.path.join(outputDir,outputXml)
    
    print inputRawXML
    print inputRawIMG
    print outputRaw
    print outputXml
    
    inputRawMeta = minidom.parse(inputRawXML)
    itemlist = inputRawMeta.getElementsByTagName('Extents')

    dataDimX = int(itemlist[0].firstChild.nodeValue)
    dataDimY = int(itemlist[1].firstChild.nodeValue)
    dataDimZ = int(itemlist[2].firstChild.nodeValue)

    print "X: " + str(dataDimX)
    print "Y: " + str(dataDimY)
    print "Z: " + str(dataDimZ)

    fileobj = open(inputRawIMG, 'r') 
    data = numpy.fromfile(fileobj, dtype='<f4')
    fileobj.close()
    
    print data.size
    print data.dtype
    data = data.reshape((dataDimZ, dataDimY, dataDimX)) 
    print data.shape
    tuples = numpy.nonzero(data)
    
    print tuples                   

    # Pull Min/Max Values
    zVals = tuples[0]
    zMin = numpy.min(zVals)
    zMax = numpy.max(zVals)
    
    yVals = tuples[1]
    yMin = numpy.min(yVals)
    yMax = numpy.max(yVals)
    
    xVals = tuples[2]
    xMin = numpy.min(xVals)
    xMax = numpy.max(xVals)

    # Crop
    lz, ly, lx = data.shape
    print data.shape
    
    # Crop X Vars
    print "x-axis min :" + str(xMin)
    print "x-axis max :" + str(xMax)
    
    # Crop Y Vars
    print "y-axis min :" + str(yMin)
    print "y-axis max :" + str(yMax)
    
    # Crop Z Vars
    print "z-axis min :" + str(zMin)
    print "z-axis max :" + str(zMax)
    data = data[zMin:zMax, yMin:yMax, xMin:xMax]
    print data.size;
    print data.shape;

    shutil.copyfile(inputRawXML,outputXml)
    
    outputRawMeta = minidom.parse(outputXml)
    itemlist = outputRawMeta.getElementsByTagName('Extents')
    itemlist[0].firstChild.nodeValue = data.shape[2]
    itemlist[1].firstChild.nodeValue = data.shape[1]
    itemlist[2].firstChild.nodeValue = data.shape[0]
    
    newXML = open(outputXml,'w')
    outputRawMeta.writexml(newXML, encoding="UTF-8")
    newXML.close()
    
    data.tofile(outputRaw)
    
    print "#@@# " + outputXml + " #@@#"

main()
            
