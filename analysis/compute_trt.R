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

# testretest.R
# Created by Greg Kiar on 2015-07-31.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

source('/Users/gkiar/code/m2g/analysis/reliability.R') #need to fix hard paths
source('/Users/gkiar/code/m2g/analysis/load_graphs.R')
dir = '/Users/gkiar/code/scratch/smg'

format = 'graphml' #graph format
rois = 70 #number of regions in graphs
scans = 2 #scans per subject
rule <- list('_', 2, 3) #subject id rule in the form of: delimiter, start, end

if (format != 'graphml') {
  stop('Currently support only exists for graphml format. Sorry') 
}

cur <- getwd()
setwd(dir)
format <- paste('\\.', format, '$', sep='')
graph_files <- list.files(pattern=format, recursive=TRUE)

pair <- load_graphs(graph_files, rois)
pair <- remove_nulls(pair[[1]], pair[[2]])
graphs <- pair[[1]]
ids <- clean_ids(pair[[2]], rule)

dist <- compute_distance(graphs)
rdf <- compute_rdf(dist, ids, scans)
mnr <- compute_mnr(rdf)
