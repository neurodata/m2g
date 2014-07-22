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

// radioselect.js
// Created by Disa Mhembere on 2014-07-20.
// Email: disa@jhu.edu
// Copyright (c) 2014. All rights reserved.

function checkBigGraphSelected()
{
  /**
   * Check if the big graph radion select box has been chosen
   */
  var radios = document.getElementsByName("Select_graph_size"); // Will have big and small radios
  for (var i=0; i < radios.length; i++) {

    if (radios[i].checked == true && radios[i].value == "big") {
      return true;
    }
  }
  return false;
}
