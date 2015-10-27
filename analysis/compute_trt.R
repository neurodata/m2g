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

# compute_trt.R
# Created by Greg Kiar on 2015-07-31.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

#parse commandline args
args <- commandArgs(TRUE)
l <- length(args)

#we need at least 2: m2g_path and graphs
if (l < 2) {
	stop(c('Please provide data and script paths in order to run, as follows:\n',
				' Rscript compute_trt.R m2g_path graphs [extension rois scans]'))
} else {
	#first variable is path to m2g base 
  scripts <- c(paste(args[1], '/analysis/load_graphs.R', sep=""), paste(args[1],'/analysis/reliability.R', sep=""))
	source(scripts[1])
	source(scripts[2])


	if (args[2] == "-l"){
		offset=1
	} else {
		offset=0
	}
	
	#set number of rois in graphs
	if (l >= 3+offset){
		rois <- strtoi(args[3+offset])
	} else {
		rois <- 70
	}
	
	#set graph format
	if (l >= 4+offset){
		format <- args[4+offset]
	} else {
		format <- 'graphml'
	}

	#set number of scans per subject
	if (l >= 5+offset){
		scans <- strtoi(args[5+offset])
	} else{
		scans <- 2
	}

	#set delimeter rule for finding ids in file names
	rule <- list('_', 2, 3)#1, 2) #subject id rule in the form of: delimiter, start, end
	
	print("Computing test-retest reliability with the following options:")
	print(paste("m2g location:", args[1]))
	print(paste("Number of rois:", rois))
	print(paste("Graph format:", format))
	print(paste("Number of scans per subject:", scans))

	if (format != 'graphml') {
  	stop('Currently support only exists for graphml format. Sorry') 
	}

	#get list of graph files in memory	
	if (args[2] == "-l" && l < 3) {
		#raised listfile flag, but no listfile to be found
		stop("Provided flag for list file, but none provided")
	} else if (args[2] == "-l") {
		#load list file
		fh <- file(args[3])
		graph_files <- readLines(fh)
		close(fh)
		print(graph_files[1:3])
	} else {
		#no flag means a directory is provided, so load from dir
		format <- paste('\\.', format, '$', sep='')
		graph_files <- list.files(path=args[2], pattern=format, recursive=TRUE, full.names=TRUE)
		print(graph_files[1:3])
	}
}


#load graph and id pairs from files
pair <- load_graphs(graph_files, rois)
pair <- remove_nulls(pair[[1]], pair[[2]])
graphs <- pair[[1]]
ids <- clean_ids(pair[[2]], rule)

#compute RDF and MNR for raw graphs
dist <- compute_distance(graphs)
rdf <- compute_rdf(dist, ids, scans)
mnr <- compute_mnr(rdf, output=TRUE)


### Suggested alternatives: log distances, nbin, and plotting

#compute RDF and MNR for log graphs
#log_graphs <- log(graphs+array(rep(1, length(graphs)), dim(graphs)), base=10)
#logdist <- compute_distance(log_graphs)
#logrdf <- compute_rdf(logdist, ids, scans)
#logmnr <- compute_mnr(logrdf, output=TRUE)

#find nbin* through means of optimizing MNR
#rank_graphs <- rank_matrices(graphs, normalize=TRUE)
#stack <- compute_nbinstar(rank_graphs, ids, scans=2, N=16, spacing="linear", lim=4900)

#compile results
#reliability <- c( mnr, logmnr)#, stack[[4]] )
#names(reliability) <-c( 'raw', 'log_raw')#, stack[[5]] )

#hist <- rbind(rdf, logrdf)#, stack[[3]])

#plot + compare the results
#library(ggplot2)
#qplot(seq_along(reliability), reliability, ylim=range(c(0.9, 1))) + scale_x_discrete(labels = names(reliability)) +
#  ggtitle("MNR of SWU_4 DTI dataset through m2g") + xlab('number of bins')
#
#plot(stats::density(logrdf[which(!is.nan(logrdf))])) +  title('RDF')
#lines(stats::density(stack[[3]][which(!is.nan(stack[[3]]))]), col=2)
#lines(stats::density(logrdf[which(!is.nan(logrdf))]), col=3)
#legend('topleft', c('raw', 'log_raw', 'nbin*'))
