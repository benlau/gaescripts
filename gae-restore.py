#!/usr/bin/python
# -*- coding: utf-8 -*-

# Restore date to server

import time
import codecs

from optparse import make_option, OptionParser
import sys
from GaeApp import GaeApp
import os
from StringIO import StringIO
import re

app = GaeApp(name="gae-restore")
app.set_usage("usage : %s <application root> <backup folder_or_file> ... " % app.name)

(options,args) = app.parse()

if len(args) < 2:
    app.help()
    sys.exit(0)

app.load()

app.connect(debug = options.debug,url=options.url,email = options.email)
print "Connected to %s at %s" % (app.app_id,app.host)



from django.conf import settings
from google.appengine.ext import db
from django.utils import simplejson
from utils import BackupFile

if not hasattr(settings , 'GAE_BACKUP_MODELS'):
    print 'GAE_BACKUP_MODELS is not defined' 
    sys.exit(0)
    
GAE_BACKUP_MODELS = settings.GAE_BACKUP_MODELS

model_classes = []
for entry in GAE_BACKUP_MODELS:
    __import__(entry[0])
    for model in entry[1]:
        model_classes.append( db._kind_map[model] )

args.pop(0)
  
def restore(input):
    if not os.path.exists(input):
        print "Warning! %s is not existed." % input
        return
    if not os.path.isdir(input):
        print "Loading %s" % input
        
        file = BackupFile(input)
        result = file.load()
        
        model_class = file.get_model_class()        
        print "Uploading data to %s..." % model_class.kind()
        app.upload_model(model_class,result)
    else:
        regexp = re.compile("^.*\.json$")
        for file in os.listdir(input):
            if regexp.match(file):
                restore(input +"/" +file)
  
for input in args:
    restore(input)

  
    
    
