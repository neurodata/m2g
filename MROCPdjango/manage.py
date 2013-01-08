#!/usr/bin/env python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: The django management module
"""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocpipeline.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
