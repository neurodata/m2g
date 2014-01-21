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
  Project_Type = forms.ChoiceField([('public', 'public'), ('private','private')],  required=False)

  # Name project
  UserDefprojectName  = forms.CharField(label='Project name', max_length=255, required = True, help_text= " ", error_messages={'required': 'You must enter a Project name'})
  site = forms.CharField(label='Enter Site', max_length=255, required = True, help_text= " ", error_messages={'required': 'You must enter a site'})
  subject = forms.CharField(label='Enter Subject ID', max_length=255, required = True , help_text= " ", error_messages={'required': 'You must enter a Subject ID'})
  session = forms.CharField(label='Enter Session ID', max_length=255, required = True, help_text= " ", error_messages={'required': 'You must enter a Session ID'})
  scanId = forms.CharField(label='Scan ID', max_length=255, required = True, help_text= " ", error_messages={'required': 'You must enter a Scan ID'})

  # Upload project files
  fiber_file = forms.FileField(label='Select fiber.dat file', required = True, help_text= "<br/> ", error_messages={'required': 'You must upload a fiber tract file'})
  roi_raw_file = forms.FileField(label='Select roi.raw file', required = True, help_text= " ", error_messages={'required': 'You must upload ROIs'})
  roi_xml_file = forms.FileField(label='Select roi.xml file', required = True, help_text= " ", error_messages={'required': 'You must upload ROIs'})

  INVARIANT_CHOICES = (('ss1', 'Scan Statistic 1',), ('tri', 'Triangle Count',), \
  ('cc', 'Clustering co-efficient',), ('mad', 'Maximum Average Degree',) \
  ,('deg', 'Vertex Degree',), ('eig', 'Top 100 (or max possible) Eigenvalues and Eigenvectors',))
  #, \
  #('ss2', 'Scan Statistic 2 [Not yet available]',), ('apl', 'Average Path Length [Not yet available]',),\
  #('gdia', 'Graph Diameter [Not yet available]',))

  # Select size of graph
  Select_graph_size = forms.ChoiceField(choices=[('small','Small graph [~30 min processing time]'), ('big','Big graph [~1.5 hr] processing time')]\
                                        , widget=RadioSelect, required = True, error_messages={'required': 'You must choose a graph size'})

  Email = forms.EmailField(widget=TextInput(), help_text= " ", required=False)

  Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=False,
  widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

  def __init__(self, *args, **kwargs):
    super(BuildGraphForm, self).__init__(*args, **kwargs)
    self.fields['Project_Type'].widget.attrs['disabled'] = True # radio / checkbox


class ConvertForm(forms.Form):
  '''
  This form will be used for uploading an invariant/graph and converting it to another file format

  @cvar FORMAT_CHOICES: The file format choices currently available i.e I{mat}, I{csv}, I{npy}
  @cvar FILE_TYPES: The file types available correspond directly to the invariants that can be computed

  @var fileObj: The file to be uploaded
  @type fileObj: file or zip file
  '''
  fileObj = forms.FileField(label='Upload data', help_text=' ', required = True)

  FORMAT_CHOICES = (('.npy', 'Numpy format (.npy)',), ('.mat', 'Matlab format (.mat)',), \
      ('.csv', '(Excel) Comma separated values (.csv)',))

  FILE_TYPES = [('cc','Clustering Coefficient'), ('deg','Local Degree'),\
      ('eig','Largest Eigenvalues/Eigenvectors'),\
      ('ss1', 'Scan Statistic 1'), ('tri','Triangle Count'),\
      ('svd','Single Value Decomposition'), ('mad', 'Maximum Average Degree'), \
      ('fg', 'Fiber Graph'), ('lcc', 'Largest Connected Component')]

  Select_file_type = forms.ChoiceField(choices=FILE_TYPES, widget=RadioSelect, help_text=' ')

  Select_conversion_format = forms.MultipleChoiceField(required=True, \
  widget=CheckboxSelectMultiple, choices=FORMAT_CHOICES)

class GraphUploadForm(forms.Form):
  '''
  This form will be used for uploading an already built graph & then giving options for
  desired invariants to be computed

  @cvar INVARIANT_CHOICES: The current invariants that can be computed by the MROCP
  '''
  fileObj = forms.FileField(label='Upload data', required=True)

  graph_format = forms.ChoiceField(required=True, widget=Select, choices=(('mat', 'MAT'), ('graphml', 'GRAPHML')), label="Graph format", error_messages={"required":"You must specify graph type"})

  # Select size of graph
  email = forms.EmailField(widget=TextInput(), required=True)

  INVARIANT_CHOICES = (('ss1', 'Scan Statistic 1',), ('tri', 'Triangle Count',), \
      ('cc', 'Clustering co-efficient',), ('mad', 'Maximum Average Degree',) \
      ,('deg', 'Vertex Degree',), ('eig', 'Top-k Eigenvalues and Eigenvectors',))

  Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=True,
  widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

  #def clean(self):
    #cleaned_data = super(GraphUploadForm, self).clean()

    #if cleaned_data['Select_graph_size'] == 'big' and not cleaned_data['Email']:
    #  raise forms.ValidationError("You must provide an email address when computing invariants on big graphs")
    #return cleaned_data

class DownloadForm(forms.Form):
  '''
  Used on confirmdownload page to choose whether to convert any invariant formats
  and how the user would like the result back i.e download as zip or see directory
  '''

  INVARIANT_CONVERSION_CHOICES = (('.mat', 'Matlab format (.mat)',), ('.csv', '(Excel) Comma separated values (.csv) [LCC and SVD Not available yet]',))

  GRAPH_CONVERSION_CHOICES = (('.npy', 'Numpy format (.npy)',), ('.csv', '(Excel) Comma separated values (.csv) [Not yet available]',))

  OUPUT_TYPES = [('dz','Download all data as zip'), ('vd','View directory with all data')]


  Select_Invariant_conversion_format = forms.MultipleChoiceField(required=False, \
  widget=CheckboxSelectMultiple, choices=INVARIANT_CONVERSION_CHOICES)

  Select_Graph_conversion_format = forms.MultipleChoiceField(required=False, \
  widget=CheckboxSelectMultiple, choices=GRAPH_CONVERSION_CHOICES)

  Select_output_type = forms.ChoiceField(choices=OUPUT_TYPES, widget=RadioSelect, required=True)
