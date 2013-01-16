#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: All forms required for web services
"""

from django import forms # for UploadFileForm
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple

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

    # Name project
    UserDefprojectName  = forms.CharField(label='Project name', help_text=' ', max_length=255, required = True, error_messages={'required': 'You must enter a Project name'})
    site = forms.CharField(label='Enter Site', help_text=' ', max_length=255, required = True, error_messages={'required': 'You must enter a site'})
    subject = forms.CharField(label='Enter Subject ID', help_text=' ', max_length=255, required = True , error_messages={'required': 'You must enter a Subject ID'})
    session = forms.CharField(label='Enter Session ID', help_text=' ', max_length=255, required = True, error_messages={'required': 'You must enter a Session ID'})
    scanId = forms.CharField(label='Scan ID', help_text='<br/>', max_length=255, required = True, error_messages={'required': 'You must enter a Scan ID'})

    # Upload project files
    fiber_file = forms.FileField(label='Select fiber.dat file', help_text=' ', required = True , error_messages={'required': 'You must upload a fiber tract file'})
    roi_raw_file = forms.FileField(label='Select roi.raw file', help_text=' ', required = True, error_messages={'required': 'You must upload ROIs'})
    roi_xml_file = forms.FileField(label='Select roi.xml file', help_text='<br/>', required = True, error_messages={'required': 'You must upload ROIs'})

    INVARIANT_CHOICES = (('SS1', 'Scan Statistic 1',), ('TriCnt', 'Triangle Count',), \
        ('CC', 'Clustering co-efficient',), ('MAD', 'Maximum Average Degree',) \
        ,('Deg', 'Vertex Degree',), ('Eigs', 'Top 100 Eigenvalues and Eigenvectors',), \
        ('SS2', 'Scan Statistic 2 [Not yet available]',), ('APL', 'Average Path Length [Not yet available]',),\
        ('GDia', 'Graph Diameter [Not yet available]',))

    Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=False,
    widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

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

    FILE_TYPES = [('cc','Clustering Coefficient'), ('deg','Local Degree'), ('eig','Largest Eigenvalues'), ('apl','Average Path Length'),\
        ('ss1', 'Scan Statistic 1'),('ss2', 'Scan Statistic 2'),('tri','Triangle Count'),('svd','Single Value Decomposition'), \
        ('mad', 'Maximum Average Degree'), ('fg', 'Fiber Graph'), ('lcc', 'Largest Connected Component')]

    Select_file_type = forms.ChoiceField(choices=FILE_TYPES, widget=forms.RadioSelect())

    Select_conversion_format = forms.MultipleChoiceField(required=True, \
    widget=CheckboxSelectMultiple, choices=FORMAT_CHOICES)

class GraphUploadForm(forms.Form):
    '''
    This form will be used for uploading an already built graph & then giving options for
    desired invariants to be computed

    @cvar INVARIANT_CHOICES: The current invariants that can be computed by the MROCP
    '''
    fileObj = forms.FileField(label='Upload data', help_text=' ', required = True)

    INVARIANT_CHOICES = (('SS1', 'Scan Statistic 1',), ('TriCnt', 'Triangle Count',), \
        ('CC', 'Clustering co-efficient',), ('MAD', 'Maximum Average Degree',) \
        ,('Deg', 'Vertex Degree',), ('Eigs', 'Top 100 Eigenvalues',), \
        ('SS2', 'Scan Statistic 2 [Not yet available]',), ('APL', 'Average Path Length [Not yet available]',),\
        ('GDia', 'Graph Diameter [Not yet available]',))

    Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=True,
    widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)


class OKForm(forms.Form):
    '''
    This form will be used for picking file return type
    of computed products after building a graph
    '''

    pass #DM TODO: Track responses to zip or view as dir structure
