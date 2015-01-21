#!/usr/bin/python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to synchronize alter the mysql database backend as neccessary
"""

from subprocess import call
import MySQLdb
import os
import argparse
from ocpipeline.settings_secret import DATABASES

def manageMRDjango(alter=False):

  manageFn =  os.path.join(os.path.abspath('.'),'manage.py')
  call( ['python', manageFn, 'syncdb'] ) # sync the DB

  if alter:
    db = MySQLdb.connect(host = 'localhost',
                           user = DATABASES['default']['USER'],
                           passwd = DATABASES['default']['PASSWORD'],
                           db = DATABASES['default']['NAME'])

    cur = db.cursor()
    cur.execute("ALTER TABLE ocpipeline_ownedprojects ADD UNIQUE INDEX(project_name, owner_id);")
    db.close() # close connection

def main():
  parser = argparse.ArgumentParser(description='Run the python database synchronizer with some extra flags if necessary')
  parser.add_argument('--alter', '-a', action='store_true', help='use this flag if you want to alter the tables for referencial integrity etc. Only necessary once')

  result = parser.parse_args()
  manageMRDjango(result.alter)

if __name__ == '__main__':
  main()