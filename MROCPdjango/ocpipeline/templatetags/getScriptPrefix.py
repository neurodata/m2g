#!/usr/bin/python

# getScriptPrefix.py
# Created by Disa Mhembere on 2013-03-17.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.

from django import template
from django.template.defaultfilters import stringfilter
from django.core.urlresolvers import get_script_prefix

register = template.Library()


@register.filter(name='getScriptPrefix', is_safe=True)
@stringfilter
def getScriptPrefix(tailurl):
  '''
  Custom filter used to get the script prefix of a certain url
  @param tailurl: the tail of the url
  @return str: the fully built url
  '''
  return get_script_prefix() + tailurl
