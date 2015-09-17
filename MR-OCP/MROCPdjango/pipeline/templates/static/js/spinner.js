
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

// spinner.js
// Created by Disa Mhembere on 2015-05-20.
// Email: disa@jhu.edu
// Copyright (c) 2015. All rights reserved.

function showSpinner( show ) {
  show = typeof show !== 'undefined' ? show : true;
  if ( show == true ) {
    document.getElementById('loadingImage').style.visibility='visible';
  } else {
    document.getElementById('loadingImage').style.visibility='hidden';
  }
}