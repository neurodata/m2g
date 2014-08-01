// Copyright 2014 Open Connectome Project (http://openconnecto.me)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// example.cpp
// Created by Disa Mhembere on 2014-07-30.
// Email: disa@jhu.edu
// Copyright (c) 2014. All rights reserved.

// Dependencies:
// - clang compiler VERSION_NUM+
// - openMP version VERSION_NUM+

// Citation:
// - None

// This is an example C++ code that computes the out degree of every node

#include <map>
#include <fstream>
#include <iostream>
#include <vector>

/**
  * \brief Compute the out-degree of the graph given an edgelist.
  * \param graph_file_name The name of the graph file on disk.
  * \return A vector with the out-degree of each node.
  */
std::vector<size_t> compute_out_degree(std::string graph_file_name) {
  std::ifstream graph_file(graph_file_name);
  std::string line; 
  std::string token;
  std::map<size_t, size_t> deg_map;

  while (std::getline(graph_file, line)) {
    token = line.substr(0, line.find(" "));
    size_t src = std::atol(token.c_str());
    if (deg_map.count(src) > 0) {
      deg_map[src] = deg_map[src] + 1;
    }
    else {
      deg_map[src] = 1;
    }
  }
  
  std::vector<size_t> ret;
  ret.resize(deg_map.size());
  for (std::map<size_t, size_t>::iterator it = deg_map.begin(); it!=deg_map.end(); ++it) {
    ret[it->first] = it->second; 
#if 0
    std::cout << it->first << " => " << it->second << '\n';
#endif 
  }
  return ret;
}

int main(int argc, char** argv) 
{
  if (argc < 2) {
    fprintf(stderr, "[Usage ERROR]: ./example graph_file_name\n");
    fprintf(stderr, "**NOTE:** The format of `graph_file_name` must be in edge list format\n");
    exit(0);
  }
  compute_out_degree(argv[1]);
}
