#!/usr/bin/python


from sys import argv
import os

params = list(argv)
inimg = params[1]
f = params[2]
g = params[3]
outf = params[4]
mask = params[5]

#print 'input image: ' + inimg
#print 'output brain image: ' + outf
#print 'output brain mask image: ' + mask

[root, ext1] = os.path.splitext(outf)
print ext1
[root, ext2] = os.path.splitext(root)
print ext2
os.system('bet '+inimg+' '+outf+' -f '+f+' -g '+g+' -m')
print 'mv '+root+'_mask'+ext2+ext1+' '+mask
os.system('mv '+root+'_mask'+ext2+ext1+' '+mask)