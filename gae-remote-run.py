#!/usr/bin/python

# Run script on remote server

from optparse import make_option, OptionParser
import sys
import os
from GaeApp import GaeApp

option_list = [
    make_option("-d", "--debug",
        action="store_true",  dest="debug",default=False),
    make_option("-u", "--url",
        action="store", type="string", dest="url",default="localhost:8000"),                    
    make_option("-e", "--email",
        action="store", type="string", dest="email"),                         
]

parser = OptionParser(option_list = option_list,usage="usage: gae-remote-run <application root> module")
(options , args ) = parser.parse_args()

if len(args) < 2:
    parser.print_help()
    sys.exit(0)

util = args[1]
app = GaeApp(args[0])
args.pop(0)
args.pop(0)

app.load()

app.connect(debug = options.debug,url=options.url,email = options.email)

print "Connected to %s at %s" % (app.app_id,app.host)

sys.path.append(os.getcwd())

script = __import__(util)

if hasattr(script,"run"):
    script.run(*args)
