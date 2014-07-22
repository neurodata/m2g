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

// checkbox.js
// Created by Disa Mhembere on 2014-07-20.
// Email: disa@jhu.edu
// Copyright (c) 2014. All rights reserved.

function moreThanChecked(form, num) 
{
// Used to tell me if more than some number of checkboxes
//  have been checked

  var checkboxes = new Array();
  var count = 0;

  checkboxes = form.getElementsByTagName('input');
  for (var i = 0; i < checkboxes.length; i++) {
    if (checkboxes[i].type === 'checkbox') {
      if (checkboxes[i].checked == true) {
        count++;
      }
      if (count > num) { // breaks loop
        fadeEffect.init('emailID', 1); // In fader.js
        document.getElementById("emailID").hidden = "";
        return true;
      }
    }
  }
  fadeEffect.init('emailID', 0);
  return false;
}

function toggleOthers(form)
{
  var checkboxes = new Array();
  checkboxes = form.getElementsByTagName('input');

  for (var i = 0; i < checkboxes.length; i++) {
    if (checkboxes[i].type === 'checkbox') {
      if (checkboxes[i].checked == true) {
        checkboxes[i].checked = false;
      }
      else {
        checkboxes[i].checked = true;
      }
    }
  }
}
