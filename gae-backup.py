#!/usr/bin/python
# -*- coding: utf-8 -*-

# Backup from server

import time
import codecs

timestamp = time.strftime("%Y-%m-%d-%H:%M", time.localtime());

from optparse import make_option, OptionParser
import sys
from GaeApp import GaeApp
import os
from StringIO import StringIO

option_list = [
    make_option("-d", "--debug",
        action="store_true",  dest="debug",default=False),
    make_option("-u", "--url",
        action="store", type="string", dest="url",default="localhost:8000"),                    
    make_option("-e", "--email",
        action="store", type="string", dest="email"),                         
]

parser = OptionParser(option_list = option_list,usage="usage: gae-backup <application root>")
(options , args ) = parser.parse_args()

if len(args) != 1:
    parser.print_help()
    sys.exit(0)

app = GaeApp(args[0])

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

if os.path.exists(timestamp):
    print "The path %s is existed. " % timestamp
    sys.exit(0)

os.mkdir(timestamp)

def default(o):
	"""
	``default(obj)`` is a function that should return a serializable version
    of obj or raise TypeError for JSON generation
    """

	if isinstance(o,db.GeoPt):
		return (o.lat,o.lon)
	elif isinstance(o,db.Key):
		return o.name()
	else:
		raise TypeError("%r is not JSON serializable" % (o,))
  
for model_class in model_classes:
    result = app.download_model(model_class)
    entities = []
    for row in result:
        entity = createEntity(row)
        entities.append(entity)
                
    text = StringIO()
	
    simplejson.dump(entities,text,default=default,ensure_ascii=False)

    filename = timestamp + "/%s.json" % model_class.kind()
    print "Writing changes to %s" % filename
    file = codecs.open(filename ,"wt","utf-8")
    file.write(text.getvalue())
    file.close()
