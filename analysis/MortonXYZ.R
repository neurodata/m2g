mortonXYZ <- function(pos) {
  x = c()
  y = c()
  z = c()
  idx <- DecToBin(pos)
  idx <- strsplit(idx, '')
  idx <- idx[[1]]
  idx <- idx[(length(idx)-24+1):length(idx)]
  length(idx)
  while (!is.na(idx[1])) {
    z <- c(z, idx[1])
    y <- c(y, idx[2])
    x <- c(x, idx[3])
    idx = idx[4:length(idx)]
  }
  triple <- c(BinToDec(x), BinToDec(y), BinToDec(z))
  return(triple)
}

DecToBin <- function(x) {
  paste(sapply(strsplit(paste(rev(intToBits(x))),""),`[[`,2),collapse="")
}

BinToDec <- function(x) {
  sum(2^(which(rev(unlist(strsplit(as.character(x), "")) == 1))-1))
}
