# Copyright 2016 NeuroData (http://neurodata.io))
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

# reliability.R
# Created by Greg Kiar on 2015-08-04.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

compute_rdf <- function(dist, ids, scans=2) {
  N <- dim(dist)[1]
  if (dim(dist)[1] != dim(dist)[2]) {
    stop('Input must be a square matrix.')
  }
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

compute_mnr <- function(rdf, remove_outliers=TRUE, thresh=0.5, output=FALSE) {
  if (remove_outliers) {
    mnr <- mean(rdf[which(rdf[!is.nan(rdf)] > thresh)])
    ol <- length(which(rdf<thresh))
    if (output) {
      print(paste('Graphs with reliability <',thresh,'(outliers):', ol))
    }
  } else {
    ol <- 0
    mnr <- mean(rdf[!is.nan(rdf)])
  }
  nopair <- length(rdf[is.nan(rdf)])
  if (output) {
    print(paste('Graphs with unique ids:',nopair))
    print(paste('Graphs available for reliability analysis:', length(rdf)-ol-nopair))
    print(paste('MNR:', mnr))
  }
  return(mnr)
}

compute_distance <- function(graphs, normx='F') {
  S <- dim(graphs)[3]
  dist <- matrix(rep(0, S*S), ncol=S)
  for (i in 1:dim(graphs)[3]) {
    for (j in i:dim(graphs)[3]) {
      dist[i,j] <- norm(graphs[,,i]-graphs[,,j], normx)
    }
  }
  dist <- dist + t(dist)
  return(dist)
}

rank_matrices <- function(graphs, normalize=FALSE) {
  d <- dim(graphs)
  rg <- array(rep(NaN, d[1]*d[2]*d[3]), d)
  for (i in 1:d[3]) {
    rg[,,i] <- array(rank(graphs[,,i], ties.method="average"), c(d[1], d[2]))
    if (normalize) {
      rg[,,i] <- ( rg[,,i] - min(rg[,,i]) ) / (max(rg[,,i]) - min(rg[,,i]))
    }
  }
  return(rg)
}

compute_nbinstar <- function(graphs, ids, scans=2, N=100, spacing='linear', lim=0) {
  require(emdbook)
  if (spacing != 'log' && spacing != 'linear') {
    stop(paste('Unknown spacing type:', spacing))
  }
  d <- dim(graphs)
  king <- 0
  if (lim) {
    set <- unique(round(lseq(2, lim, N)))
  } else {
    set <- 2:N
  }
  mnrs <- array(rep(NA, length(set)), length(set))
  print(set)
  for (i in set) {
    if (spacing=='log') {
      bs <- lseq(1/i, 1-1/i, i-1)
    } else {
      bs <- seq(1/i, 1-1/i, length.out=i-1)
    }
    tempg <- array(rep(0, d[1]*d[2]*d[3]), d)
    for (j in 1:length(bs)) {
      tempg <- tempg + (graphs > bs[j])
    }
    tempd <- compute_distance(tempg, norm='F')
    mnrs[i] <- compute_mnr(compute_rdf(tempd, ids, scans))
    print(mnrs[i])
    if (mnrs[i] > king) {
      king <- mnrs[i]
      kingbins <- bs
      kingrdf <-compute_rdf(tempd, ids, scans)
    }
  }
  mnrs<-mnrs[which(!is.na(mnrs))]
  pack <- list(king, kingbins, kingrdf, mnrs, set)
  return(pack)
}
