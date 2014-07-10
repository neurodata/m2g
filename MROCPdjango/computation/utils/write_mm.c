#include <igraph.h>
#include <stdio.h>

int main(int argc, char* argv[])
{
  igraph_i_set_attribute_table(&igraph_cattribute_table);
  char * in_graph_fn;
  char * out_graph_fn;

  if (argc < 3) {
    printf("[ERROR] usage: mm-writer in_graph_fn out_graph_fn\n");
    exit(-1);
  }
  else {
    in_graph_fn = &argv[1][0];
    out_graph_fn = &argv[2][0];
  }
  
  igraph_t g;
  
  FILE *ifile, *ofile;

  ifile = fopen(in_graph_fn, "r");
  if (ifile == 0) {
    return 10;
  }
  
  igraph_read_graph_graphml(&g, ifile, 0);
  fclose(ifile);
  igraph_to_directed(&g, IGRAPH_TO_DIRECTED_ARBITRARY);

  printf("The graph stats:\n");
  printf("Vertices: %li\n", (long int) igraph_vcount(&g));
  printf("Edges: %li\n", (long int) igraph_ecount(&g));
  printf("Directed: %i\n", (int) igraph_is_directed(&g));
  
  ofile = fopen(out_graph_fn, "w");
  if (ofile == 0) {
    return 10;
  }
  
  // Write MM format
  fprintf(ofile, "%li %li %li\n", (long int) igraph_vcount(&g),
      (long int) igraph_vcount(&g), (long int) igraph_ecount(&g));

  igraph_integer_t to;
  igraph_integer_t from;
  igraph_integer_t eid;
  igraph_real_t weight;

  for (eid = 0; eid < (long int) igraph_ecount(&g); eid++) {
    igraph_edge(&g, eid, &from, &to);
    weight = igraph_cattribute_EAN(&g, "weight",eid);
    fprintf(ofile, "%i %i %f\n", from, to, weight);

    //printf("Edge %i => %i --> %i\n", eid, from, to);
    //printf("Edge %i has weight %f\n", eid, igraph_cattribute_EAN(&g, "weight",eid)); // TODO: time
  }

  // For all. TODO: time
  igraph_es_t eids;
  igraph_es_all(&eids, IGRAPH_EDGEORDER_ID); // Order edges 

  igraph_vector_t result;
  igraph_vector_init(&result, (int long) igraph_ecount(&g));
  igraph_cattribute_EANV(&g, "weight", eids, &result);
  
  igraph_integer_t i;
  for (i = 0; i < (int long) igraph_ecount(&g); i++)
     printf("Edge %i value: %f\n", i, VECTOR(result)[i]);
  
  // Free memory
  igraph_es_destroy(&eids);
  igraph_vector_destroy(&result);
  igraph_destroy(&g);

  fclose(ofile);
  return 0;
}
