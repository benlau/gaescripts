#!/usr/bin/python
# -*- coding: utf-8 -*-

# Backup from server

import time
import codecs
import datetime

timestamp = time.strftime("%Y-%m-%d-%H:%M", time.localtime());

from optparse import make_option, OptionParser
import sys
from GaeApp import GaeApp
import os
from StringIO import StringIO

option_list = [
    make_option("-o", "--output",
        help="The output path of backup.",
        default = None,
        action="store", type="string", dest="output"),                             
]

app = GaeApp(name="gae-backup.py")
app.add_options(option_list)
(options,args) = app.parse()

app.load()

app.connect(debug = options.debug,url=options.url,email = options.email)

print "Connected to %s at %s" % (app.app_id,app.host)

from django.conf import settings
from google.appengine.ext import db
from utils import serialize
from django.utils import simplejson
from google.appengine.api.users import User

if not hasattr(settings , 'GAE_BACKUP_MODELS'):
    print 'GAE_BACKUP_MODELS is not defined' 
    sys.exit(0)
    
GAE_BACKUP_MODELS = settings.GAE_BACKUP_MODELS

model_classes = []
for entry in GAE_BACKUP_MODELS:
    __import__(entry[0])
    for model in entry[1]:
        model_classes.append( db._kind_map[model] )


if options.output:
    output_path = options.output
else:
    output_path = timestamp

if not os.path.exists(output_path):
    os.mkdir(output_path)

def default(o):
    """
    ``default(obj)`` is a function that should return a serializable version
    of obj or raise TypeError for JSON generation
    """

    if isinstance(o,db.Key):
        return o.id_or_name()
    else:
        raise TypeError("%r is not JSON serializable" % (o,))   
  
for model_class in model_classes:
    filename = output_path + "/%s.json" % model_class.kind()
    print "Saving changes to %s" % filename    
    result = app.download_model(model_class)
    entities = []
    for row in result:
        entity = serialize(row)
        entities.append(entity)
                
    text = StringIO()
	
    simplejson.dump(entities,text,default=default,ensure_ascii=False,indent =1)

    file = codecs.open(filename ,"wt","utf-8")
    file.write(text.getvalue())
    file.close()
