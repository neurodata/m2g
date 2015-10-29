# lcc.R
# Created by Disa Mhembere on 2015-04-09.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

require(igraph)
lcc <- function(gfn) {
  g <- read.graph(gfn, format="graphml")
    comp <- components(g, mode="weak")
    which(comp$membership == which.max(comp$csize))
}
