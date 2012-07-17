'''
This form has only one field. See Form FileField reference for details.
'''
from django import forms # for UploadFileForm

class DocumentForm(forms.Form): 
    docfile = forms.FileField(label='Select fiber.dat file', help_text='                          ', required = True)
    roi_raw_file = forms.FileField(label='Select roi.raw file', help_text='                          ', required = True)
    roi_xml_file = forms.FileField(label='Select roi.xml file', help_text='                          ', required = True)
    error_css_class = 'error'
    required_css_class = 'required'

class DataForm(forms.Form):
    UserDefprojectName  = forms.CharField(label='Project name   ', help_text='                          ', max_length=255, required = True, error_messages={'required': 'Please your Project name'})
    site = forms.CharField(label='Enter Site   ', help_text='                          ', max_length=255, required = True)
    subject = forms.CharField(label='Enter Subject ID  ', help_text='                          ', max_length=255, required = True)
    session = forms.CharField(label='Enter Session ID ', help_text='                          ', max_length=255, required = True)
    scanId = forms.CharField(label='Scan ID  ', help_text='                          ', max_length=255, required = True)

class OKForm(forms.Form):
    projectName  = forms.BooleanField(label='Do you accept the data   ',
                        error_messages={'required': 'Please select yes or no'},
                            help_text="You cannot obtain data without yes")