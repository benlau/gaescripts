#!/usr/bin/python

# Run script on remote server

from optparse import make_option, OptionParser
import sys
from GaeApp import GaeApp

option_list = [
    make_option("-d", "--debug",
        action="store_true",  dest="debug",default=False),
    make_option("-u", "--url",
        action="store", type="string", dest="url",default="localhost:8000"),                    
    make_option("-e", "--email",
        action="store", type="string", dest="email"),                         
]

parser = OptionParser(option_list = option_list,usage="usage: gae-remote-run <application root>")
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

if not hasattr(settings , 'GAE_BACKUP_MODELS'):
    print 'GAE_BACKUP_MODELS is not defined' 
    sys.exit(0)
    
GAE_BACKUP_MODELS = settings.GAE_BACKUP_MODELS

# Start backup

for model in GAE_BACKUP_MODELS:
    model_class = db._kind_map[model]
    
    while entities:
        for entry in entities:
            agency.append(entry)

        entities = Agency.all().filter('__key__ >', entities[-1].key()).fetch(100)
