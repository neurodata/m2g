#!/usr/bin/python

# graph_table.py
# Created by Disa Mhembere on 2014-02-13.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import django_tables2 as tables
from models import GraphDownloadModel
import os
from django.utils.safestring import mark_safe
from urlparse import urlparse


class GraphTable(tables.Table):

  selection = tables.CheckBoxColumn(accessor="pk", orderable=False, visible=True)

  class Meta:
    #self.selection.visible = True
    model = GraphDownloadModel
    attrs = {"class" : "paleblue"} # Set table class in html to paleblue
    #td__input
    # Specify which fields to display in table
    fields = ("selection", "url", "region", "numvertex", "numedge",
        "graphattr", "vertexattr", "edgeattr", "sensor", "source")
    order_by = ("url")

  def set_html_name(self, name):
    self.html_name = name

  def render_url(self, value):
    # TODO: Figure out how to better alter the rendered html than mark_safe
    txt = os.path.splitext(os.path.basename(value))[0].capitalize() # Shorten what I see
    return mark_safe("<a href=\"%s\">%s</a>" %(value, txt))

  def render_source(self, value):
    # TODO: Figure out how to better alter the rendered html than mark_safe
    netloc = urlparse(value).netloc
    if not netloc: netloc = "Link"
    return mark_safe("<a href=\"%s\">%s</a>" % (value, netloc))
