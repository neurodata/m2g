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

manageFn =  os.path.join(os.path.abspath('.'),'manage.py')
call( ['python', manageFn, 'syncdb'] ) # sync the DB


db = MySQLdb.connect(host="localhost",
                     user="root",
                      passwd="",
                      db="MRdjango")

cur = db.cursor()

# So as to avoid truncation errors
cur.execute("ALTER TABLE ocpipeline_convertmodel MODIFY COLUMN filename TEXT;")
cur.execute("ALTER TABLE ocpipeline_document MODIFY COLUMN docfile TEXT;")
