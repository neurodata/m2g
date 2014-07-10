LDFLAGS=-L /usr/local/lib
INCFLAGS=-I /usr/local/include/igraph
CC=clang
DEBUGFLAG=-g

all: mm-writer

mm-writer: write_mm.c
	$(CC) write_mm.c 	$(LDFLAGS) $(INCFLAGS) -ligraph -o mm-writer

clean:
	rm mm-writer
