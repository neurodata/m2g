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
from views import showdir
from views import contact
from views import jobfailure
from views import download
from views import igraph_examples

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ocpipeline.views',
    url(r'^$', 'default', name= 'default'),
    url(r'^welcome/$', 'welcome', name= 'welcome'),
    url(r'^success/$', 'success', name='success-page'),
    url(r'^confirmdownload/$', 'confirmDownload', name='confirm-dwnd-page'),
    url(r'^processinput/$', 'processInputData', name='process-input-data'),
    url(r'^zipoutput/$','zipProcessedData', name = 'zip-processed-data'), # 2nd param function is view, 3rd param - anything
    url(r'^upload/(.*$)', 'upload', name= 'prog-upload'),
    url(r'^graphupload/(.*$)', 'graphLoadInv', name= 'graph-upload-invariant-processing'),
    url(r'^download/(.*$)', 'download', name= 'download-graphs'),
    url(r'^convert/(.*$)', 'convert', name= 'convert-to-format'),
    url(r'^buildgraph/$', 'buildGraph', name= 'build-graph'),
    url(r'^showdir/$', 'showdir', name='serve-dir'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^jobfailure/$', 'jobfailure', name='failure-page'),
    url(r'^igraph/$', 'igraph_examples', name='igraph-examples'),
    (r'^accounts/', include('registration.backends.default.urls')),
    # Examples
    # url(r'^$', 'myapp.views.home', name='home'),
    # url(r'^myapp/', include('myapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from ocpipeline.accounts.views import projects
urlpatterns +=patterns('ocpipeline.accounts.views',
                      url(r'^accounts/projects/$', 'projects', name='project-accounts'),
                       )

'''
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/$', 'login', name='login'),
    url(r'^accounts/logout/$', 'logout', name='logout'),
    url(r'^accounts/password_change/$', 'password_change', name='password_change'),
    url(r'^accounts/password_change/done/$', 'password_change_done', name='password_change_done'),
    url(r'^accounts/password_reset/$', 'password_reset', name='password_reset'),
    url(r'^accounts/password_reset/done/$', 'password_reset_done', name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$', 'password_reset_complete', name='password_reset_complete'),
)
'''
