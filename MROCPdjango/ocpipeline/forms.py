#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: All forms required for web services
"""

from django import forms
from django.forms.fields import MultipleChoiceField, BooleanField, ChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, Select, SelectMultiple, TextInput

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

  @var roi_raw_file: Fiber tract xml file
  @type roi_raw_file: string

  @var roi_xml_file: Fiber tract roi file
  @type roi_xml_file: string

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
  UserDefprojectName  = forms.CharField(label='Project name', max_length=255, required = True, error_messages={'required': 'You must enter a Project name'})
  site = forms.CharField(label='Enter Site', max_length=255, required = True, error_messages={'required': 'You must enter a site'})
  subject = forms.CharField(label='Enter Subject ID', max_length=255, required = True , error_messages={'required': 'You must enter a Subject ID'})
  session = forms.CharField(label='Enter Session ID', max_length=255, required = True, error_messages={'required': 'You must enter a Session ID'})
  scanId = forms.CharField(label='Scan ID', max_length=255, required = True, error_messages={'required': 'You must enter a Scan ID'})

  # Upload project files
  fiber_file = forms.FileField(label='Select fiber.dat file', required = True, error_messages={'required': 'You must upload a fiber tract file'})
  roi_raw_file = forms.FileField(label='Select roi.raw file', required = True, error_messages={'required': 'You must upload ROIs'})
  roi_xml_file = forms.FileField(label='Select roi.xml file', required = True, error_messages={'required': 'You must upload ROIs'})

  INVARIANT_CHOICES = (('ss1', 'Scan Statistic 1',), ('tri', 'Triangle Count',), \
  ('cc', 'Clustering co-efficient',), ('mad', 'Maximum Average Degree',) \
  ,('deg', 'Vertex Degree',), ('eig', 'Top-k Eigenvalues and Eigenvectors',))

  Select_graph_size = forms.ChoiceField(choices=(('small','Small graph [~7 min]'), ('big','Big graph [~20 min]'))
                                  , widget=RadioSelect, required = True, error_messages={'required': 'You must choose a graph size'})

  Email = forms.EmailField(widget=TextInput(), required=False)

  Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=False,
  widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

  def __init__(self, *args, **kwargs):
    super(BuildGraphForm, self).__init__(*args, **kwargs)
    self.fields['Project_Type'].widget.attrs['disabled'] = 'disabled' # radio / checkbox


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
            ('npy', 'numpy format (npy)'), ('mat', 'MATLAB format (mat)')]

  input_format = forms.ChoiceField(required=True, widget=Select, choices=IN_FORMATS, label="Input format")

  OUT_FORMATS = IN_FORMATS[:-3]
  OUT_FORMATS.extend([('dot', 'dot'), ('gml', 'gml'), ('leda', 'leda')])

  output_format = forms.MultipleChoiceField(required=True, \
  widget=SelectMultiple, choices=OUT_FORMATS, label="Output file format")

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
  email = forms.EmailField(widget=TextInput(), required=True)

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

  OUPUT_TYPES = [('dz','Download all data as zip'), ('vd','View directory with all data')]

  Select_output_type = forms.ChoiceField(choices=OUPUT_TYPES, widget=RadioSelect, required=True)

class DownloadGraphs(forms.Form):
  """
  Form for download in
  """

  def set_name(self, name):
    self.form_name = name


