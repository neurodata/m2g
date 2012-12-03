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
    UserDefprojectName  = forms.CharField(label='Project name   ', help_text='                          ', max_length=255, required = True, error_messages={'required': 'Please enter your Project name'})
    site = forms.CharField(label='Enter Site   ', help_text='                          ', max_length=255, required = True)
    subject = forms.CharField(label='Enter Subject ID  ', help_text='                          ', max_length=255, required = True)
    session = forms.CharField(label='Enter Session ID ', help_text='                          ', max_length=255, required = True)
    scanId = forms.CharField(label='Scan ID  ', help_text='                          ', max_length=255, required = True)

class MyForm(forms.Form):
    my_field = forms.MultipleChoiceField(choices=SOME_CHOICES, widget=forms.CheckboxSelectMultiple())

    def clean_my_field(self):
        if len(self.cleaned_data['my_field']) > 3:
            raise forms.ValidationError('Select no more than 3.')
        return self.cleaned_data['my_field']



class OKForm(forms.Form):
    pass #DM TODO: Track responses to zip or view as dir structure
    