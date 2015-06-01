#!/usr/bin/env python 

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Read a fiber file and generate the corresponding sparse graph
# @author Randal Burns, Disa Mhembere


import argparse
from mrcap.fiber import FiberReader
import mrcap.roi as roi
from time import time
from computation.utils.cmdline import parse_dict

def genGraph(infname, data_atlas_fn, outfname, bigGraph=False, \
    outformat="graphml", numfibers=0, centroids=True, graph_attrs={}, **atlases):
  """
	Generate a sparse igraph from an MRI file based on input and output names.
  
	We traverse fiber streamlines and map the voxels which they pass through to a brain region, as determined by an atlas. Big graphs have ROIs which are single voxels, whereas small graphs' ROIs are much larger and can be determined either by size, function, or any other method. Outputs a graphml formatted graph by default.

	**Positional Arguments**

			infname: [.dat; binary file]
					- MRIStudio format fiber streamlines.
			data_atlas_fn: [.nii; nifti image]
					- Region labels which will be used to parcellate the fibers.
	
	**Returns**
	
			outfname: [.graphml; XML file]
					- Generated graph from fiber tracts.

	**Optional Arguments**
	
			bigGraph: [boolean] (default = False)
					- Flag indicating where to process a bigGraph=True or smallGraph=False.
			outformat: [string] (default = graphml)
					- Requested output format of graph. 	
			numfibers: [int] (default = 0)
					- The number of fibers to read/process. If 0, process all fibers.
			centroids: [boolean] (default = True)
					- Flag indicating whether to add centroids for the graph.
			graph_attrs: [dictionary] (default = {})
					- Dict with graph attributes to be added with key=attr_name, value=attr_value.
			atlases: [dictionary] (default = {})
					- Dict with key=atlas_fn, value=region_name_fn
  """

  start = time()
  # Determine size of graph to be processed i.e pick a fibergraph module to import
  if bigGraph: from fibergraph_bg import FiberGraph
  else: from fibergraph_sm import FiberGraph

  # This ensures there is at least one atlas by default now
  if data_atlas_fn not in atlases:
    print "Adding default atlas"
    atlases[data_atlas_fn] = None

  rois = roi.ROIData(data_atlas_fn)

  # Create fiber reader
  reader = FiberReader(infname)

  # DM FIXME: Hacky -- we no longer read shape from fiber file so this happens :-/
  reader.shape = rois.data.shape

  # Create the graph object
  # get dims from reader
  fbrgraph = FiberGraph (reader.shape, rois)

  print "Parsing MRI studio file {0}".format (infname)

  # Print the high-level fiber information
  print "Reader Header", reader

  count = 0

  # iterate over all fibers
  for fiber in reader:
    count += 1
    # add the contribution of this fiber to the
    fbrgraph.add(fiber)
    if numfibers > 0 and count >= numfibers:
      break
    if count % 10000 == 0:
      print ("Processed {0} fibers".format(count))

  del reader
  # Done adding edges
  fbrgraph.complete(centroids, graph_attrs, atlases)

  fbrgraph.saveToIgraph(outfname, gformat=outformat)

  del fbrgraph
  print "\nGraph building complete in %.3f secs" % (time() - start)
  return

def main ():

  parser = argparse.ArgumentParser(description="Read the contents of MRI Studio file \
      and generate a sparse connectivity graph using igraph with default \
      output format 'graphML'")
  parser.add_argument("fbrfile", action="store", help="The fiber file name")
  parser.add_argument("data_atlas", action="store", help="The atlas with region data")
  parser.add_argument("output", action="store", help="resulting name of graph")

  parser.add_argument( "--outformat", "-f", action="store", default="graphml", \
      help="The output graph format i.e. graphml, gml, dot, pajek etc..")
  parser.add_argument( "--isbig", "-b", action="store_true", default=False, \
      help="Is the graph big? If so use this flag" )
  parser.add_argument("-a", "--atlas", nargs="*", action="store", default=[], \
      help ="Pass atlas filename(s). If regions are named then pass region \
      naming file as well in the format: '-a atlas0 atlas1,atlas1_region_names \
      atlas2 atlas3,atlas3_region_names' etc.")
  parser.add_argument( "--centroids", "-C", action="store_true", \
      help="Pass to *NOT* include centroids" )
  parser.add_argument( "-G", "--graph_attrs", nargs="*", default=[], action="store", \
      help="Add (a) graph attribute(s). Quote, use colon for key:value and spaces \
      for multiple e.g 'attr1:value1' 'attr2:value2'")
  parser.add_argument("--numfib", "-n", action="store", type=int, default=0, \
      help="The number of fibers to process before exit")

  result = parser.parse_args()

  # Add atlases to a dict
  atlas_d = {}
  for atl in result.atlas:
    sp_atl = atl.split(",")
    if len(sp_atl) == 2: atlas_d[sp_atl[0]] = sp_atl[1]
    elif len(sp_atl) == 1: atlas_d[sp_atl[0]] = None

  # Parse dict
  result.graph_attrs = parse_dict(result.graph_attrs)

  genGraph(result.fbrfile, result.data_atlas, result.output, result.isbig, 
      result.outformat, result.numfib, not result.centroids, result.graph_attrs, **atlas_d)

if __name__ == "__main__":
  main()
