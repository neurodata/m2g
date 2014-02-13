-- create_graph_table.sql
-- author: Disa Mhembere
-- email: disa@jhu.edu
-- Create a `graphs' database for storing the graphs we host
-- run with: mysql -u <uname> -p mrdjango < create_graph_table.sql

drop table if exists graphs;
create table graphs(
filepath varchar(1024) not null,
genus varchar(128),
region varchar(128),
numvertex bigint not null,
numedge bigint not null,
graphattr text, -- I will use JSON encoded string to store
vertexattr text, 
edgeattr text,
sensor varchar(64),
source varchar(256),
mtime double -- Modification time
);
