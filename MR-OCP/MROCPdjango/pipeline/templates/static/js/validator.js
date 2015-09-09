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

// validator.js
// Created by Disa Mhembere on 2014-07-20.
// Email: disa@jhu.edu
// Copyright (c) 2014. All rights reserved.

function Validate(oForm, _validFileExtensions) {
  var arrInputs = oForm.getElementsByTagName("input");
  for (var i = 0; i < arrInputs.length; i++) {
    var oInput = arrInputs[i];
    if (oInput.type == "file") {
      var sFileExt = oInput.value.split('.').pop().toLowerCase();
      var blnValid = false;
      for (var j = 0; j < _validFileExtensions.length; j++) {
        var sCurExtension = _validFileExtensions[j];

        if ( sFileExt == sCurExtension.toLowerCase()) {
          blnValid = true;
          break;
        }
      }

      if (!blnValid) {
        showSpinner(false);
        alert("Sorry, " + oInput.value.split("\\").pop() + " is invalid, allowed extensions are: " + _validFileExtensions.join(", "));
        return false;
      }
    }
  }
  return true;
}

function checkEmail(email) {
  /**
   *  Validate if input email matches know a@b.com format
   *  @param email: The email input node
   */
  var filter = /^([a-zA-Z0-9_.-])+@(([a-zA-Z0-9-])+.)+([a-zA-Z0-9]{2,4})+$/;
  if (!filter.test(email.value)) {
    alert('The scale or quantity of grahs you selected dictates you must provide a valid email address! e.g john@gmail.com');
    email.focus;
    return false;
  }
  return true;
}

