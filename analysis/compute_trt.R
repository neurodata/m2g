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

source('/Users/gkiar/code/ocp/FlashR/stats/reliability.R') #need to fix hard paths
source('/Users/gkiar/code/ocp/m2g/analysis/load_graphs.R')

dir <- '/Users/gkiar/code/ocp/scratch/m2g/smg'
format <- 'graphml' #graph format
rois <- 70 #number of regions in graphs
scans <- 2 #scans per subject
rule <- list('_', 2, 3) #subject id rule in the form of: delimiter, start, end

if (format != 'graphml') {
  stop('Currently support only exists for graphml format. Sorry') 
}

#get list of graph files
cur <- getwd()
setwd(dir)
format <- paste('\\.', format, '$', sep='')
graph_files <- list.files(pattern=format, recursive=TRUE)

#load graph and id pairs from files
pair <- load_graphs(graph_files, rois)
pair <- remove_nulls(pair[[1]], pair[[2]])
graphs <- pair[[1]]
ids <- clean_ids(pair[[2]], rule)

#compute RDF and MNR for raw graphs
dist <- compute_distance(graphs)
rdf <- compute_rdf(dist, ids, scans)
mnr <- compute_mnr(rdf)

#compute RDF and MNR for log graphs
log_graphs <- log(graphs+array(rep(1, length(graphs)), dim(graphs)), base=10)
logdist <- compute_distance(log_graphs)
logrdf <- compute_rdf(logdist, ids, scans)
logmnr <- compute_mnr(logrdf)

#find nbin* through means of optimizing MNR
rank_graphs <- rank_matrices(graphs, normalize=TRUE)
stack <- compute_nbinstar(rank_graphs, ids, scans=2, N=16, spacing="linear", lim=4900)

#compile results
reliability <- c( mnr, logmnr, stack[[4]] )
names(reliability) <-c( 'raw', 'log_raw', stack[[5]] )

hist <- rbind(rdf, logrdf, stack[[3]])

#plot + compare the results
library(ggplot2)
qplot(seq_along(reliability), reliability, ylim=range(c(0.9, 1))) + scale_x_discrete(labels = names(reliability)) +
  ggtitle("MNR of SWU_4 DTI dataset through m2g") + xlab('number of bins')
#
#plot(stats::density(logrdf[which(!is.nan(logrdf))])) +  title('RDF')
#lines(stats::density(stack[[3]][which(!is.nan(stack[[3]]))]), col=2)
#lines(stats::density(logrdf[which(!is.nan(logrdf))]), col=3)
#legend('topleft', c('raw', 'log_raw', 'nbin*'))
