#!/usr/bin/Rscript
# a utility to convert from csv to rds
# written by Eric Bridgeford
# usage:
#   ./csv2rds.R csvfile.csv rdsfile.rds

readcsv <- function(filename) {
    data <- readLines(file(filename, 'r'))
    return(matrix(as.numeric(unlist(strsplit(data, split="\\s+"))), nrow=length(data), byrow=TRUE))
}

args <- commandArgs(trailingOnly = TRUE)
csvpath <- args[[1]]
rdspath <- args[[2]]

csvobj <- readcsv(csvpath)
saveRDS(csvobj, rdspath)

