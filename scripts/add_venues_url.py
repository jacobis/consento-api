# encoding: utf-8

'''
Created on Dec 5, 2014

@author: Jacob Sungwoon Lee
'''

import os.path
import sys
import time


print "Create bulk objects for Venue... "

t = time.time()

abspath = os.path.dirname(os.path.abspath(sys.argv[0]))
path = os.path.join(abspath, 'development/data/2014_and_2014_additional_image_data.py')
execfile(path)
Venue.objects.bulk_create(data)

print "Task Complete! Execution time : %.02fs" % (time.time() - t)