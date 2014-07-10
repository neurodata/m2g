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

LDFLAGS=-L /usr/local/lib
INCFLAGS=-I /usr/local/include/igraph
CC=clang
DEBUGFLAG=-g

all: mm-writer

mm-writer: write_mm.c
	$(CC) write_mm.c 	$(LDFLAGS) $(INCFLAGS) -ligraph -o mm-writer

clean:
	rm mm-writer
