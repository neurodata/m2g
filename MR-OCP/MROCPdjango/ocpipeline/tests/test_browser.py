# /usr/bin/env python

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
#

import pytest

class TestServices:

  def test_home(self, client):
    response = client.get("/", follow=True)
    assert response.status_code == 200

  # FIXME
  def test_build_graph(self, client):
    fiber = open("/data/MR.new/fiber/M87102806_fiber.dat")
    fiber = fiber.read()


    response = client. post("/buildgraph", 
        {
          "scanId" : "test_scan",
          "site" : " test_site",
          "subject": "test_subj",
          "session" : "test_sess",
          "UserDefprojectName" : "test_proj",
           "Select_graph_size": "small",
           "fiber_file": fiber,
           },
        follow=True)


    print response.content
    assert response.status_code == 200

