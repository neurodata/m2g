
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
# Created by Disa Mhembere
# Email: disa@jhu.edu
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to hold url patterns for one-click MR-connectome pipeline
"""

from django.conf.urls import patterns, include, url
from views import success
from views import showdir
from views import contact
from views import jobfailure
from views import igraph_examples

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ocpipeline.views',
    url(r'^$', 'default', name= 'default'),
    url(r'^welcome/$', 'welcome', name= 'welcome'),
    url(r'^success/$', 'success', name='success-page'),
    url(r'^upload/(.*$)', 'upload', name= 'prog-upload'),
    url(r'^showdir/$', 'showdir', name='serve-dir'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^jobfailure/$', 'jobfailure', name='failure-page'),
    url(r'^igraph/$', 'igraph_examples', name='igraph-examples'),

    url(r'^data/human/$', 'human_data_descrip', name='human-data-descrip'),
    (r'^accounts/', include('registration.backends.default.urls')),
    # Examples
    # url(r'^$', 'myapp.views.home', name='home'),
    # url(r'^myapp/', include('myapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from ocpipeline.proc_views.buildgraph import buildGraph
urlpatterns += patterns('ocpipeline.proc_views.buildgraph',
    url(r'^buildgraph/$', 'buildGraph', name= 'build-graph'),
    )

from ocpipeline.proc_views.graphupload import graphLoadInv
urlpatterns += patterns('ocpipeline.proc_views.graphupload',
    url(r'^graphupload/(.*$)', 'graphLoadInv', name='graph-upload-invariant-processing'),
    )

from ocpipeline.proc_views.download import download
urlpatterns += patterns('ocpipeline.proc_views.download',
    url(r'^download/$', 'download', name= 'download-graphs'),
    )

from ocpipeline.proc_views.convert_graph import convert_graph
urlpatterns += patterns('ocpipeline.proc_views.convert_graph',
    url(r'^convert/(.*$)', 'convert_graph', name= 'convert-to-format'),
    )

from ocpipeline.accounts.views import projects
urlpatterns +=patterns('ocpipeline.accounts.views',
    url(r'^accounts/projects/$', 'projects', name='project-accounts'),
    )

