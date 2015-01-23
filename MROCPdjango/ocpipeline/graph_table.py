#!/usr/bin/env python

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

# graph_table.py
# Created by Disa Mhembere on 2014-02-13.
# Email: disa@jhu.edu

import django_tables2 as tables
from models import GraphDownloadModel
import os
from django.utils.safestring import mark_safe
from urlparse import urlparse

class GraphTable(tables.Table):
  selection = tables.CheckBoxColumn(accessor="pk", orderable=False, visible=True,
                  attrs={"th":{"onclick":"toggleOthers(this.parentNode.parentNode.parentNode.\
                      parentNode.parentNode); moreThanChecked(document.\
                      getElementById('Human').getElementsByTagName('form')[0], 1);"}})

  #factor = tables.TemplateColumn(temp, "factor_template", orderable=False, visible=True, accessor="pk",)

  class Meta:
    model = GraphDownloadModel
    attrs = {"class" : "paleblue"} # Set table class in html to paleblue

    # Specify which fields to display in table
    fields = ("selection", "url", "region", "numvertex", "numedge",
        "graphattr", "vertexattr", "edgeattr", "sensor", "project", "source")
    order_by = ("project")

  def set_html_name(self, name):
    self.html_name = name

  def render_url(self, value):
    # TODO: Figure out how to better alter the rendered html than mark_safe
    txt = os.path.splitext(os.path.basename(value))[0].capitalize() # Shorten what I see
    if txt[-24:] == "_big_graph_w_inv.graphml": txt = txt[:-24]
    return mark_safe("<a href=\"%s\">%s</a>" %(value, txt))

  def render_source(self, value):
    # TODO: Figure out how to better alter the rendered html than mark_safe
    netloc = urlparse(value).netloc
    if not netloc: netloc = "Link"
    return mark_safe("<a href=\"%s\">%s</a>" % (value, netloc))
