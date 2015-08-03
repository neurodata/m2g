
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


trt <- function(dir, format='graphml'){ # dir = base directory for graphs; format = graph format
format = 'graphml'
dir = '/Users/gkiar/code/scratch/smg'

	if (format != 'graphml') {
		stop('Currently support only exists for graphml format. Sorry') 
	}
	cur <- getwd()
	setwd(dir)
	format <- paste('\\.', format, '$', sep='')
	graph_files <- list.files(pattern=format, recursive=TRUE)
	
	pair <- load_graphs(graph_files, 70)
	graphs <- pair[[1]]
	
	rule <- list('_', 2, 3) #delimiter, start, end
	ids <- clean_ids(pair[[2]], rule)
	
	dist <- compute_distance(graphs)
	rdf <- compute_rdf(dist, ids, 2)
	print(rdf)
	MNR <- mnr(rdf)
}


compute_rdf <- function(dist, ids, scans=2) {
	N <- dim(dist)[1]
	rdf <- array(NaN, N*(scans-1))
	count <- 1
	for (i in 1:N) {
		ind <- which(ids==ids[i])
		for (j in ind) {
			if (j != i) {
				di <- dist[i,]
				di[ind] <- Inf
				d <- dist[i,j]
				rdf[count] <- 1 - (sum(di[!is.nan(di)] < d) + 0.5*sum(di[!is.nan(di)] == d)) / (N-length(ind))
				count <-  count + 1
			}
		}
	}
	return(rdf)
}

mnr <- function(rdf, remove_outliers=TRUE) {
  if (remove_outliers) {
    mnr <- mean(rdf[which(rdf[!is.nan(rdf)] > 0.5)])
    print(paste('Removed', length(which(rdf<0.5)), 'outliers from', length(!is.nan(rdf))))
  } else {
    mnr <- mean(rdf[!is.nan(rdf)])
  }
  print(paste('MNR:', mnr))
  return(mnr)
}

compute_distance <- function(graphs) {
  S <- dim(graphs)[3]
  dist <- matrix(rep(0, S*S), ncol=S)
  for (i in 1:dim(graphs)[3]) {
    for (j in i:dim(graphs)[3]) {
      dist[i,j] <- norm(graphs[,,i]-graphs[,,j], 'F')
    }
  }
  dist <- dist + t(dist)
  return(dist)
}

load_graphs <- function(fnames, rois) {
	require('igraph')
	# N <- length(fnames)
	N <- 50
	graphs <- array(rep(NaN, rois*rois*N), c(rois, rois, N))
	ids <- array(NaN, N)
	for (i in 1:N) {
	  res <- try(tempg <- read.graph(fnames[i], format='graphml'))
	  if (inherits(res, 'try-error')) {
	    print(paste('The following graph failed to load:', fnames[i]))
	  }
	  else {
	    tempg <- get.adjacency(tempg, type='upper', attr='weight', sparse=FALSE)
	    if (all(dim(tempg) != c(rois,rois))) {
	      warning(paste('The following graph is the impropper size:', fnames[i]))
	      next;
	    }
	    if (sum(tempg) < 1e6) {
	      warning(paste('The following graph has suspiciously few edges', fnames[i]))
	      next;
	    }
	    graphs[,,i] <- tempg
	    ids[i] <- fnames[i]
	  }
	}
	pair <- list(graphs, ids)
	return(pair)
}

clean_ids <- function(ids, rule){
	N <- length(ids)
	clean_id <- array(NaN, N)
	for (i in 1:N) {
	  if (is.nan(ids[i])){
	    clean_id[i] <- NaN
	  }
		ind <- which(strsplit(ids[i], "")[[1]]==rule[[1]])
		clean_id[i] <- substr(ids[i], ind[rule[[2]]]+1, ind[rule[[3]]]-1)
	}
	
	return(clean_id)
}


#trt('/Users/gkiar/code/scratch/smg')
