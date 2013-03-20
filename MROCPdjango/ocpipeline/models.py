#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to alter/update the MRdjango database as necessary
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
  Allows us to store data on build graph view
  '''
  project_name = models.CharField(max_length=255)
  site = models.CharField(max_length=255,)
  subject = models.CharField(max_length=255,)
  session = models.CharField(max_length=255,)
  scanId = models.CharField(max_length=255)
  location = models.TextField()
  owner = models.CharField(max_length=30, null=True, default="NULL")

class OwnedProjects(models.Model):
  project_name = models.CharField(max_length=255)
  owner = models.ForeignKey(auth_user, username) # Many-to-one . Many here, other in auth_user
  is_private = models.BooleanField(null=False)
  owner_group = models.CharField(max_length=255, null=True) # Will reference other table soon


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
