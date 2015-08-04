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

# reliability.R
# Created by Greg Kiar on 2015-08-04.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

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

compute_mnr <- function(rdf, remove_outliers=TRUE, thresh=0.5) {
  if (remove_outliers) {
    mnr <- mean(rdf[which(rdf[!is.nan(rdf)] > thresh)])
    ol = length(which(rdf<thresh))
    nopair = length(rdf[is.nan(rdf)])
    print(paste('Graphs with unique ids:',nopair))
    print(paste('Graphs with mnr <',thresh,'(outliers):', ol))
    print(paste('Remaining graphs available for processing:', length(rdf)-ol-nopair))
  } else {
    mnr <- mean(rdf[!is.nan(rdf)])
  }
  print(paste('MNR:', mnr))
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