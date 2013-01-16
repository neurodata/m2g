"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to hold url patterns for one-click MR-connectome pipeline
"""

from django.conf.urls import patterns, include, url
from views import buildGraph
from views import success
from views import zipProcessedData
from views import processInputData
from views import confirmDownload
from views import graphLoadInv
from views import convert

#########################################
from ocpipeline.views import buildGraph
#########################################

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ocpipeline.views',
    url(r'^$', 'default', name= 'welcome'),
    url(r'^success/$', 'success', name='success-page'),
    url(r'^confirmdownload/$', 'confirmDownload', name='confirm-dwnd-page'),
    url(r'^processinput/$', 'processInputData', name='process-input-data'),
    url(r'^zipoutput/$','zipProcessedData', name = 'zip-processed-data'), # 2nd param function is view, 3rd param - anything
    url(r'^upload/(.*$)', 'upload', name= 'prog-upload'),
    url(r'^graphupload/(.*$)', 'graphLoadInv', name= 'graph-upload-invariant-processing'),
    url(r'^convert/(.*$)', 'convert', name= 'convert-to-format'),
    url(r'^buildgraph/$', 'buildGraph', name= 'build-graph'),
    # Examples
    # url(r'^$', 'myapp.views.home', name='home'),
    # url(r'^myapp/', include('myapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)