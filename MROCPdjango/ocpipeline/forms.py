'''
This form has only one field. See Form FileField reference for details.
'''
from django import forms # for UploadFileForm
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

#from models import Document

class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select fiber.dat file', help_text='                          ', required = True)
    roi_raw_file = forms.FileField(label='Select roi.raw file', help_text='                          ', required = True)
    roi_xml_file = forms.FileField(label='Select roi.xml file', help_text='                          ', required = True)
    error_css_class = 'error'
    required_css_class = 'required'

    INVARIANT_CHOICES = (('SS1', 'Scan Statistic 1',), ('TriCnt', 'Triangle Count',), \
        ('CC', 'Clustering co-efficient',), ('MAD', 'Maximum Average Degree',) \
        ,('Deg', 'Vertex Degree',), ('Eigs', 'Top 100 Eigenvalues',), \
        ('SS2', 'Scan Statistic 2',), ('APL', 'Average Path Length',),\
        ('GDia', 'Graph Diameter',))

    Select_Invariants_you_want_computed = forms.MultipleChoiceField(required=False,
    widget=CheckboxSelectMultiple, choices=INVARIANT_CHOICES)

    #class Meta:
    #    model = Document


class DataForm(forms.Form):
    UserDefprojectName  = forms.CharField(label='Project name   ', help_text='                          ', max_length=255, required = True, error_messages={'required': 'Please enter your Project name'})
    site = forms.CharField(label='Enter Site   ', help_text='                          ', max_length=255, required = True)
    subject = forms.CharField(label='Enter Subject ID  ', help_text='                          ', max_length=255, required = True)
    session = forms.CharField(label='Enter Session ID ', help_text='                          ', max_length=255, required = True)
    scanId = forms.CharField(label='Scan ID  ', help_text='                          ', max_length=255, required = True)

class OKForm(forms.Form):
    pass #DM TODO: Track responses to zip or view as dir structure
