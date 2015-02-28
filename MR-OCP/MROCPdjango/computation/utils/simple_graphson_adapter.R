
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

#!/usr/bin/env Rscript

# simple_graphson_adapter.R
# Created by Disa Mhembere on 2014-01-19.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

require(argparse)
suppressMessages(require(igraph))

IgraphToGraphson <- function(g, save_fn){
  # Simple function to write and igraph graph to GraphSON format as described
  # in https://github.com/tinkerpop/blueprints/wiki/GraphSON-Reader-and-Writer-Library
  #  * Note special edge attribute "weight" is used for weighted igraph
  # Args:
  #   g: the igraph graph
  #   save_fn: the file name you want to use to save the resulting file
  # 
  # Returns:
  #   Exit status 1 for success

# Open graph
out.str <- '{\n\t"graph": {\n' # The string that will hold the graph text
if (is.directed(g)){
  out.str <- paste0(out.str, '"edgedefault":"directed"\n')
} else {
  out.str <- paste0(out.str, '"edgedefault":"undirected"\n')
}

for (attr in list.graph.attributes(g)){
  attr.val <- get.graph.attribute(g, attr)
  if (is.na(attr.val)){ # Do nothing  
  } else if (class(attr.val) == "character"){
    # Must be a list we are encoding as a json string
    if (substr(attr.val, 1,1) == "[" & substr(attr.val, nchar(attr.val),nchar(attr.val)) == "]") {
      out.str <- paste0(out.str, sprintf('\t\t"%s":%s,\n', attr, attr.val))
    } else {
      out.str <- paste0(out.str, sprintf('\t\t"%s":"%s",\n', attr, attr.val))
    }
  } else if (class(attr.val) == "logical" | class(attr.val) == "numeric"){ # floats included here
    out.str <- paste0(out.str, sprintf('\t\t"%s":%s,\n', attr, tolower(attr.val)))  
  } else{
    cat(sprintf("Ignoring unwritable class of graph attribute '%s' ...", class(attr.val)))
  }
}

# Check vertices
if ( length(V(g)) > 0 )
{
  attrs <- list.vertex.attributes(g) # vertex attrs
  out.str <- paste0(out.str, '\t\t"vertices": [\n')
  for (vertex.id in V(g)){
    out.str <- paste0(out.str, '\t\t\t{\n', '\t\t\t\t"id":', vertex.id, ",\n")
    for (attr in attrs){
      attr.val <- get.vertex.attribute(g, attr, index=vertex.id)
      if (is.na(attr.val)){ # Do nothing  
      } else if (class(attr.val) == "character"){  
        # Must be a list we are encoding as a json string
        if (substr(attr.val, 1,1) == "[" & substr(attr.val, nchar(attr.val),nchar(attr.val)) == "]") {
          out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":%s', attr, attr.val), ",\n")
        } else {
          out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":"%s"', attr, attr.val), ",\n")
        }
      } else if (class(attr.val) == "logical" | class(attr.val) == "numeric"){ # floats included here
        out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":%s,\n', attr, tolower(attr.val)))  
      } else{
        cat(sprintf("Ignoring unwritable class of vertex attribute '%s' ...\n", class(attr.val)))
      }
    }
  out.str <- paste0(substr(out.str, 1, nchar(out.str)-2), '\n\t\t\t},\n') # Close single vertex
  }
  # Close vertices
  out.str <- paste0(substr(out.str, 1, nchar(out.str)-2), '\n\t\t]')
}

# Check edges
if (length(E(g)) > 0){
  out.str <- paste0(out.str, ',\n\t\t"edges": [\n')

  attrs <- list.edge.attributes(g) 
  all.edges <- get.edges(g, 1:ecount(g)) # All edges 
  for (row in 1:ecount(g)){
    # Add the edge
    out.str <- paste0(out.str, sprintf('\t\t\t{\n\t\t\t\t"_inV": "%d",\n\t\t\t\t"_outV": "%d",\n', all.edges[row,1], all.edges[row,2]))
    
    for (attr in attrs){
      attr.val <- get.edge.attribute(g, attr, index=row)
      if (is.na(attr.val)){ # Do nothing  
      } else if (class(attr.val) == "character"){  
        if (substr(attr.val, 1,1) == "[" & substr(attr.val, nchar(attr.val),nchar(attr.val)) == "]") {
          out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":%s', attr, attr.val), ",\n") 
        } else {
          out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":"%s"', attr, attr.val), ",\n")   
        }
      } else if (class(attr.val) == "logical" | class(attr.val) == "numeric"){ # floats included here
        out.str <- paste0(out.str, sprintf('\t\t\t\t"%s":%s,\n', attr, tolower(attr.val)))  
      } else{
        cat(sprintf("Ignoring unwritable class of edge attribute '%s' ...\n", class(attr.val)))
      }
    }
  out.str <- paste0(substr(out.str, 1, nchar(out.str)-2), '\n\t\t\t},\n') # Close single vertex
  }
  #Close Edges
  out.str <- paste0(substr(out.str, 1, nchar(out.str)-2), '\n\t\t]')
}

# Close graph
out.str <- paste0(out.str, '\n\t}\n}\n')

cat(sprintf("Writing \"%s\" to disk ...\n", save_fn))
file.conn <- file(save_fn)
writeLines(out.str, file.conn)
close(file.conn)
return(1)
}


GraphsonToIgraph <- function(fn){
  # Simple function to read a graphSON formatted graph into igraph. The graph must match the
  # specifications described at https://github.com/tinkerpop/blueprints/wiki/GraphSON-Reader-and-Writer-Library
  #  * Note special edge attribute "weight" will create a weighted igraph
  # Args:
  #   fn: the file name of the graphson file.
  # 
  # Returns:
  #   An igraph object
  
  require(rjson)
  jd <- fromJSON(paste(readLines(fn), collapse=""))
  num.nodes <- length(jd$graph$vertices)
  
  if (!is.null(jd$graph$edgedefault) | jd$graph$edgedefault == FALSE){
    directed <- FALSE
  }
  else{
    directed <- TRUE
  } 
  # Create the graph
  g <- graph.empty(n=num.nodes, directed=directed)
  
  # Add vertex attributes if any
  
  # Add edges 
  
  # Add edge attributes
  
  
}

TestWrite <- function(){
  #g <- graph.empty(0, directed=TRUE)
  g <- erdos.renyi.game(5, 6, type="gnm", directed=FALSE) 
  #g <- erdos.renyi.game(5, 0, type="gnm", directed=FALSE) 
  g <- set.graph.attribute(g, name="graph_attr", "[3,4,5,3,4]")
  g <- set.vertex.attribute(g, "test_vert_attr", value=c(1,3,5,33,2))
  
  g <- set.edge.attribute(g, "test_attr0", value=c("this", "is", "the", "way", "we", "do"))
  g <- set.edge.attribute(g, "test_attr1", value=c(12.34, 323.2, 23.3, 3432.33, 34.22, 343.76))
  g <- set.edge.attribute(g, "test_attr2", value=FALSE, index=3)
  cat("Running test function ...\n")
  IgraphToGraphson(g, "testgraph.graphson")
}

TestRead <- function(){
cat("Unimplemented ..\n") # TODO: DM
}

# ============= Main =============== #
if (!interactive())
{
  parser <- ArgumentParser(description="VERY simple reader and writer from and to igraph, graphSON format")

  parser$add_argument("-f", "--file.name", action="store", help="Pass if file is on disk and needs to be read. If passed we assume its graphSON to igraph")
  parser$add_argument("-t", "--test", action="store_true", help="If its a test pass this flag")
  result <- parser$parse_args()

  if (result$test){ # & (nchar(result$file.name)==0) ){
    TestWrite()
  }
}
