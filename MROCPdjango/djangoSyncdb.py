#!/usr/bin/python

from subprocess import call
import MySQLdb
import os

manageFn =  os.path.join(os.path.abspath('.'),'manage.py')
call( ['python', manageFn, 'syncdb'] ) # sync the DB


db = MySQLdb.connect(host="localhost",
                     user="root",
                      passwd="mysql",
                      db="MRdjango")

cur = db.cursor()

# So as to avoid truncation errors
cur.execute("ALTER TABLE ocpipeline_convertmodel MODIFY COLUMN filename TEXT;")
cur.execute("ALTER TABLE ocpipeline_document MODIFY COLUMN docfile TEXT;")
