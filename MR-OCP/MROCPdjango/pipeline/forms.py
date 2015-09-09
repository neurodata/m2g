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
#

"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: All forms required for web services
"""

from django import forms
from django.forms.fields import MultipleChoiceField, BooleanField, ChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, Select, SelectMultiple, TextInput, EmailInput

#
#class LoginForm(forms.Form):
#  username = forms.CharField(required = True, error_messages={'required': 'You must enter a username'})
#  password = forms.PasswordInput()
#
#class RegisterForm(forms.Form):
#  username = forms.CharField(required = True, error_messages={'required': 'You must enter a username'})
#  email = forms.EmailField(required = True, error_messages={'required': 'You must enter an email address'})
#  confirmEmail = forms.EmailField(required = True, error_messages={'required': 'You must enter an email address'})
#  password = forms.PasswordInput()
#  confirmPassword = forms.PasswordInput()

class LogoutForm(forms.Form):
  pass

class PasswordResetForm(forms.Form):
  username = forms.CharField(required = True, error_messages={'required': 'You must enter a username'})
  email = forms.EmailField(required = True, error_messages={'required': 'You must enter an email address'})


class BuildGraphForm(forms.Form):
  '''
  This form will be used for:
      1. Routing data correctly when building graphs.
      2. Naming projects.
      3. Uploading derivative files

  @cvar INVARIANT_CHOICES: The current invariants that can be computed by the MROCP

  @var docfile: Fiber tract file
  @type docfile: string

  @var data_atlas_file: Atlas file
  @type data_atlas_file: string

  @var UserDefprojectName: The name of the project
  @type UserDefprojectName: string

  @var site: The site where scan was done
  @type site: string

  @var subject: The ID corresponding to the subject in question
  @type subject: string

  @var session: The session ID/name
  @type session: string

  @var scanId: The scan ID of the scan session
  @type scanId: string
  '''

  # Public or private Project
  Project_Type = forms.ChoiceField([('public', 'public'), ('private','private')], widget=Select, required=False)

  # Name project
  UserDefprojectName  = forms.CharField(label='Project name', max_length=255, widget=TextInput(),
                                        required = True, error_messages={'required': 'You must enter a Project name'})
  site = forms.CharField(label='Enter Site', max_length=255, widget=TextInput(),
                         required = True, error_messages={'required': 'You must enter a site'})
  subject = forms.CharField(label='Enter Subject ID', max_length=255, widget=TextInput(),
                            required = True , error_messages={'required': 'You must enter a Subject ID'})
  session = forms.CharField(label='Enter Session ID', max_length=255, widget=TextInput(),
                            required = True, error_messages={'required': 'You must enter a Session ID'})
  scanId = forms.CharField(label='Scan ID', max_length=255, widget=TextInput(),
                           required = True, error_messages={'required': 'You must enter a Scan ID'})

  # Upload project files
  fiber_file = forms.FileField(label='Select fiber.dat file', required = True, 
      error_messages={'required': 'You must upload a fiber tract file'},)
  data_atlas_file = forms.FileField(label='Data atlas file (Optional)',required = False)

  INVARIANT_CHOICES = (('ss1', 'Scan Statistic 1',), ('tri', 'Triangle Count',), \
  ('cc', 'Clustering co-efficient',), ('mad', 'Maximum Average Degree',) \
  ,('deg', 'Vertex Degree',), ('eig', 'Top-k Eigenvalues and Eigenvectors',))

  Select_graph_size = forms.ChoiceField(choices=(('small','Small graph [~7 min]'), \
      ('big','Big graph [~20 min]')), widget=RadioSelect(), required = True, \
      error_messages={'required': 'You must choose a graph size'})

  Email = forms.EmailField(widget=EmailInput(attrs={"class":"tb", "size":35}), required=True)

  Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=False,
  widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

  def __init__(self, *args, **kwargs):
    super(BuildGraphForm, self).__init__(*args, **kwargs)
    self.fields["Project_Type"].widget.attrs["disabled"] = "disabled" # radio / checkbox


class ConvertForm(forms.Form):
  '''
  This form will be used for uploading an invariant/graph and converting it to another file format

  @cvar FORMAT_CHOICES: The file format choices currently available i.e I{mat}, I{csv}, I{npy}
  @cvar FILE_TYPES: The file types available correspond directly to the invariants that can be computed

  @var fileObj: The file to be uploaded
  @type fileObj: file or zip file
  '''
  fileObj = forms.FileField(label='Upload data', required = True)

  IN_FORMATS = [('graphml', 'graphml'), ('ncol','ncol'), ('edgelist', 'edgelist'),
            ('lgl','lgl'),('pajek', 'pajek'), ('graphdb', 'graphdb'),
            ('npy', 'numpy format (npy)'), ('mat', 'MATLAB format (mat)'), 
            ('attredge', 'Attributed edgelist')]

  input_format = forms.ChoiceField(required=True, widget=Select, choices=IN_FORMATS, label="Input format")

  OUT_FORMATS = IN_FORMATS[:-4]
  OUT_FORMATS.extend([('dot', 'dot'), ('gml', 'gml'), ('leda', 'leda')])

  output_format = forms.MultipleChoiceField(required=True, \
      widget=SelectMultiple(attrs={"class":"tb", "style":"width: 100px;"}), choices=OUT_FORMATS, label="Output file format")
  Email = forms.EmailField(widget=EmailInput(attrs={"class":"tb", "size":40}), required=True)

class GraphUploadForm(forms.Form):
  '''
  This form will be used for uploading an already built graph & then giving options for
  desired invariants to be computed

  @cvar INVARIANT_CHOICES: The current invariants that can be computed by the MROCP
  '''
  fileObj = forms.FileField(label='Upload data', required=True)

  graph_format = forms.ChoiceField(required=True, widget=Select,
      choices=(('graphml', 'graphml'), ('ncol','ncol'), ('edgelist', 'edgelist'),
      ('lgl','lgl'),('pajek', 'pajek'), ('graphdb', 'graphdb'), ('mat', 'MATLAB'),
      ('npy', 'numpy')), label="Graph format", error_messages={"required":"You must specify graph type"})

  # Select size of graph
  email = forms.EmailField(widget=EmailInput(attrs={"class":"tb", "size":35}), required=True)

  INVARIANT_CHOICES = (('ss1', 'Scan Statistic 1',), ('tri', 'Triangle Count',), \
      ('cc', 'Clustering co-efficient',), ('mad', 'Maximum Average Degree',) \
      ,('deg', 'Vertex Degree',), ('eig', 'Top-k Eigenvalues and Eigenvectors',))

  Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=True,
  widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

class DownloadForm(forms.Form):
  '''
  Used on confirmdownload page to choose whether to see results i.e download
  as zip or see directory
  '''

  OUTPUT_TYPES = [('dz','Download all data as zip'), ('vd','View directory with all data')]

  Select_output_type = forms.ChoiceField(choices=OUTPUT_TYPES, widget=RadioSelect, required=True)

class DownloadGraphsForm(forms.Form):
  """
  Form for download in
  """
  def set_name(self, name):
    self.form_name = name

  FORMATS = [('graphml', 'graphml'), ('ncol','ncol'), ('edgelist', 'edgelist'),
            ('lgl','lgl'),('pajek', 'pajek'), ('dot', 'dot'), ('gml', 'gml'),
            ('leda', 'leda'), ('mm', 'Market Matrix')]

  dl_format = forms.ChoiceField(required=True, widget=Select(
    attrs={"title":"Only graphml will contain all vertex, edge and graph attributes"}),
                                choices=FORMATS, label="Format")
  Email = forms.EmailField(widget=EmailInput(attrs={"class":"tb", "size":40}), 
      required=True, error_messages={"required":"You must supply an email address"})

class DownloadQueryForm(forms.Form):
  '''
  This form is used for querying the DB for graphs available for download.

  @cvar QUERY_ATTR: The field you want to query from
  '''
  query_type = forms.ChoiceField(required=True, widget=Select,
      choices=(('all', 'All'), ('name', 'Graph name'), ('genus','Genus'), ('region', 'Region'),
      ('numedge_gt', 'Edge count greater than'), ('numedge_lt', 'Edge count less than'),
      ('numvertex_gt','Vertex count greater than'), ('numvertex_lt','Vertex count less than'),
      ('attribute', 'Graph/Vertex/Edge Attribute'), ('sensor', 'Sensor'), ('project', 'Project'),
      ('source', 'Source'),), label="Search type", error_messages={"required":"You must specify search type"})

  # Select size of graph
  query = forms.CharField(max_length=512, required=True, widget=forms.TextInput(attrs={"class":"tb", "size":"100"}))

from fields import MultiFileField

class RawUploadForm(forms.Form):
  """
  A form for uploading raw images to be processed in to graphs
  
  @cvar niftis: The image(s) in nifti format
  @cvar bs: The b value and b vector files
  @cvar atlas: The atlas with which to build the graph
  """

  dti = forms.FileField(required=True, label="DTI")
  mprage  = forms.FileField(required=True, label="MPRAGE")
  bvalue =  forms.FileField(required=True)
  bvector = forms.FileField(required=True)

  graphsize = forms.ChoiceField(required=True, \
      widget=Select, choices=((True,"Big"), (False,"Small")), label="Graph size")

  atlas = forms.ChoiceField(required=True, \
      widget=Select, choices=(("MNI","MNI"),))

  email = forms.EmailField(widget=EmailInput(attrs={"class":"tb", "size":40}), 
      required=True, error_messages={"required":"You must supply an email address"})

