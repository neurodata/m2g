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

# load_graphs.R
# Created by Greg Kiar on 2015-08-04.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

load_graphs <- function(fnames, rois, thresh=1e5) {
  require('igraph')
  N <- length(fnames)
  size <- 0
  edges <- 0
  fail <- 0
  version
  graphs <- array(rep(NaN, as.numeric(rois*rois*N)), c(rois, rois, N))
  ids <- array(NaN, N)
  for (i in 1:N) {
    res <- try(tempg <- read.graph(fnames[i], format='graphml'))
    if (inherits(res, 'try-error')) {
      # warning(paste('The following graph failed to load:', fnames[i]))
      fail <- fail + 1
    }
    else {
      tempg <- get.adjacency(tempg, type='upper', attr='weight', sparse=FALSE)
      if (all(dim(tempg) != c(rois,rois))) {
        # warning(paste('The following graph is the impropper size:', fnames[i]))
        size <- size + 1
        next;
      }
      if (sum(tempg) < thresh) {
        # warning(paste('The following graph has suspiciously few edges', fnames[i]))
        edges <- edges + 1
        next;
      }
      graphs[,,i] <- tempg
      ids[i] <- fnames[i]
    }
  }
  print(paste('Total number of graphs found:', N))
  print(paste('Number of graphs which failed to load: ', fail))
  print(paste('Graphs with improper dimensions: ', size))
  print(paste('Graphs with less than', thresh, 'edges:', edges))
  N2 <- N - size - edges
  print(paste('Remaining graphs available for processing:', N2))
  pair <- list(graphs, ids, N2)
  return(pair)
}

clean_ids <- function(ids, rule){
  N <- length(ids)
  clean_id <- array(NaN, N)
  for (i in 1:N) {
		ids[i] <- basename(ids[i])
    if (is.nan(ids[i])){
      clean_id[i] <- NaN
    }
    ind <- which(strsplit(ids[i], "")[[1]]==rule[[1]])
    clean_id[i] <- substr(ids[i], ind[rule[[2]]]+1, ind[rule[[3]]]-1)
  }
  
  return(clean_id)
}

remove_nulls <- function(graphs, ids) {
  ind <- which(ids!="NaN")
  graphs2 <- graphs[,,ind]
  ids2 <- ids[ind]
  pair <- list(graphs2, ids2)
  return(pair)
}
