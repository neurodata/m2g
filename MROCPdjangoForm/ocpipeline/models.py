'''
FileField stores files e.g. to media/documents based MEDIA_ROOT
Generally, each model maps to a single database table.
'''
from django.db import models
from django.contrib import admin
import os
from time import strftime, localtime

projectName = ""
outputDir = 'temp/'

class Document(models.Model): # Try adding attribute class DocumentForm(forms.Form, SaveProject Name)
    global projectName
    if projectName == "":
       projectName = strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime())
        
    docfile = models.FileField(upload_to= (outputDir + projectName))
    
    # Return Location of file    
    def getProjectName(self):
        global projectName
        return projectName
    
    def __unicode__(self):
        return self.name
    
class Data(models.Model):
    projectName  = models.CharField(max_length=255)
    site = models.CharField(max_length=255,)
    subject = models.CharField(max_length=255,)
    session = models.CharField(max_length=255,)
    scanId = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
class OK(models.Model):
    projectName  = models.BooleanField()
    
    def __unicode__(self):
        return self.name
    
    
admin.site.register(Document)