
import roi
import matplotlib.pyplot

roix = roi.ROIXML( "/data/MR/roi/M87186642_roi.xml" )

rois = roi.ROIData ( "/data/MR/roi/M87186642_roi.raw", roix.getShape() ) 

print rois.data.shape
matplotlib.pyplot.pcolor ( rois.data[:,:,51] )

raw_input("Press Enter to continue...")
