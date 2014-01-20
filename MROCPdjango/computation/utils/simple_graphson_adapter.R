#!/usr/bin/env Rscript

# simple_graphson_adapter.R
# Created by Disa Mhembere on 2014-01-19.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

require(argparse)
require(igraph)

parser$add_argument("-t", "--test", action="store_true", help="If its a test pass this flag")
result <- parser$parse_args()

igraph_to_graphson <- function(g, save_fn){
out.str <- '{\n\t"graph": {\n' # The string that will hold the graph text

# Look at graph
for (attr in list.graph.attributes(g)){
  attr.val <- get.graph.attribute(g, attr)
  if (class(attr.val) == "character"){
    out.str <- paste0(out.str, sprintf('\t\t"%s":"%s"', attr, attr.val))
  } else if (class(attr.val) == "logical" | class(attr.val) == "numeric"){ # floats included here
    out.str <- paste0(out.str, sprintf('\t\t"%s":%s,\n', attr, tolower(attr.val)))  
  } else{
    cat(sprintf("Ignoring unwritable class of graph attribute '%s' ...", class(attr)))
  }
}

# Look at vertices
attrs <- list.vertex.attributes(g) # vertex attrs
out.str <- paste0(out.str, '\t\t"vertices": [\n')
for (vertex.id in V(g)){
  out.str <- paste0(out.str, '\t\t\t{\n', '\t\t\t\t"id:"', vertex.id, ",\n")
  for (attr in attrs){
    attr.val <- get.vertex.attribute(g, attr, index=c(vertex.id)) 
    if (class(attr.val) == "character"){  
      out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":"%s"', attr, attr.val), ",\n") #FIXME: Extra comma
    }
  }
  
out.str <- paste0(substr(out.str, 1, nchar(out.str)-2), '\t\t\t},\n')

}






}

test <- function(){
  g <- erdos.renyi.game(5, 6, type="gnm", directed=FALSE) 
  cat("Running test function ...\n")
  igraph_to_graphson(g, "testgraph.graphson")

}
