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

app = GaeApp(name="gae-restore")

(options,args) = app.parse()

if len(args) != 2:
    app.help()
    sys.exit(0)

backup_folder = args[1]

if not os.path.exists(backup_folder):
    print "The folder %s is not existed." % backup_folder
    sys.exit(0)


app.load()

app.connect(debug = options.debug,url=options.url,email = options.email)
print "Connected to %s at %s" % (app.app_id,app.host)



from django.conf import settings
from google.appengine.ext import db
from utils import createEntity
from django.utils import simplejson

if not hasattr(settings , 'GAE_BACKUP_MODELS'):
    print 'GAE_BACKUP_MODELS is not defined' 
    sys.exit(0)
    
GAE_BACKUP_MODELS = settings.GAE_BACKUP_MODELS

model_classes = []
for entry in GAE_BACKUP_MODELS:
    __import__(entry[0])
    for model in entry[1]:
        model_classes.append( db._kind_map[model] )
 
  
for model_class in model_classes:
    filename = backup_folder + "/%s.json" % model_class.kind()
    print "Loading %s " % filename
    try:
        file = codecs.open(filename ,"rt","utf-8")
        data=""
        for line in file:
            data+=line
        result = simplejson.loads(data)
            
        file.close()
        
        app.upload_model(model_class,result)
    except IOError:
        print "IOError. Skipped"
    
    
