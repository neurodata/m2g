#!/usr/local/bin/python2.7

from sys import argv
import numpy as np
import xml.etree.ElementTree as et
import nibabel as nib
import os

params = list(argv)

input_xml = params[1]
output_dir = params[2]

input_raw = os.path.splitext(input_xml)[0]+'.raw'

print input_xml
print input_raw
print output_dir
print

tree = et.parse(input_xml)
root = tree.getroot()

for attributes in root.findall('Dataset-attributes'):
    data_type = attributes.find('Data-type').text
    print 'data_type = ' + data_type

    image_offset = attributes.find('Image-offset').text
    print 'image_offset = ' + image_offset

    endianess = attributes.find('Endianess').text
    print "endianess = " + endianess

    extents = []
    for extent in root.iter('Extents'):
        extents.append(int(extent.text))
    print 'extents =', extents

    resolutions = []
    for resolution in root.iter('Resolution'):
        resolutions.append(resolution.text)
    print 'resolution =', resolutions

    slice_spacing = attributes.find('Slice-spacing').text
    print 'slice_spacing = ' + slice_spacing

    slice_thickness = attributes.find('Slice-thickness').text
    print 'slick_thickness = ' + slice_thickness

    units = []
    for unit in root.iter('Units'):
        units.append(unit.text)
    print 'units =', units

    compression = attributes.find('Compression').text
    print 'compression = ' + compression

    orientation = attributes.find('Orientation').text
    print 'orientation = ' + orientation

    subject_axis_orientations = []
    for sub_or in root.iter('Subject-axis-orientation'):
        subject_axis_orientations.append(sub_or.text)
    print 'subject_axis_orientations =', subject_axis_orientations

    origins = []
    for origin in root.iter('Origin'):
        origins.append(origin.text)
    print 'origins =', origins

    modality = attributes.find('Modality').text
    print 'modality = ' + modality

if data_type == 'Float':
    dataType = '<f4'

file_obj = open(input_raw, 'r')
data = np.fromfile(file_obj, dtype=dataType)


print
print 'raw size =', data.size
data = data.reshape(extents)
print data
print 'raw reshape =', data.shape
print np.nanmax(data)

img = nib.Nifti1Image(data, affine=None)

print img

file_obj.close()

out_file = os.path.join(output_dir, (os.path.splitext(os.path.basename(input_raw))[0]+'.nii.gz'))

print
print '#@@# ' + out_file + ' #@@#'

print '#@@@# ' + input_xml + ' #@@@#'

img.to_filename(out_file)








