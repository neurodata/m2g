#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to create the directories necessary for the OCPIPELINE
"""

'''
FileField stores files e.g. to media/documents based MEDIA_ROOT
Generally, each model maps to a single database table.
'''
from django.db import models
from django.contrib import admin
import os
from time import strftime, localtime

class BuildGraphModel(models.Model):
  '''
  upload_to location dynamically altered in view
  (This is a little hacky & can be done better using a custom manager)
  see: https://docs.djangoproject.com/en/dev/ref/models/instances/?from=olddocs
  '''

  derivfile = models.FileField(upload_to = (' '))

  projectName  = models.CharField(max_length=255)
  site = models.CharField(max_length=255,)
  subject = models.CharField(max_length=255,)
  session = models.CharField(max_length=255,)
  scanId = models.CharField(max_length=255)

class ConvertModel(models.Model):
  '''
  upload_to location dynamically altered in view
  '''
  filename = models.FileField(upload_to = (' '))

  def __unicode__(self):
      return self.name

class OK(models.Model):
  #DM TODO: Track responses to zip or view as dir structure
  pass

  def __unicode__(self):
      return self.name

admin.site.register(BuildGraphModel)
admin.site.register(ConvertModel)
admin.site.register(OK)
