#!/usr/bin/python

# views.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.


from django.shortcuts import render

def projects(request):

  return render(request, 'projects.html')
