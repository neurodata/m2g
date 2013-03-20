#!/usr/bin/python
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

    cur.execute("ALTER TABLE OwnedProjects ADD UNIQUE INDEX(project_name, owner);")
    cur.execute("ALTER TABLE ocpipeline_convertmodel MODIFY COLUMN filename TEXT;") # depr

    db.close() # close connection

def main():
  parser = argparse.ArgumentParser(description='Run the python database synchronizer with some extra flags if necessary')
  parser.add_argument('--alter', '-a', action='store_true', help='use this flag if you want to alter the tables for referencial integrity etc. Only necessary once')

  result = parser.parse_args()
  manageMRDjango(result.alter)

if __name__ == '__main__':
  main()
