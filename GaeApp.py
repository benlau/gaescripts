# -*- coding: utf-8 -*-

import sys
import os
import getpass
import datetime
from optparse import make_option, OptionParser

class GaeApp:
    def __init__(self,path = None , name = None):
        self.basepath = None
        
        if path:
            self.basepath = os.path.abspath(path)
        self.app_id = None
        self.name = name
        self.usage = None
        
        self.option_list = [
            make_option("-d", "--debug",
                action="store_true",  dest="debug",default=False),
            make_option("-u", "--url",
                action="store", type="string", dest="url",default="localhost:8000"),                    
            make_option("-e", "--email",
                action="store", type="string", dest="email"),                         
                
        ]
        
    def add_options(self,options):
        """
        Add options for parse function()
        """
        
        if isinstance(options,list):
            for opt in options:
                self.option_list.append(opt)
        else:
            self.option_list.append(options)
            
    def set_usage(self,usage):
        self.usage = usage
            
    def parse(self):      
        if not self.usage:
            usage = "usage : %s <application root>" % self.name
        else:
            usage = self.usage
            
        parser = OptionParser(option_list = self.option_list,usage=usage)
        (options , args ) = parser.parse_args()
        self.options = options
        self.parser = parser
        try:
            self.basepath = os.path.abspath(args[0])
        except:
            parser.print_help()
            sys.exit(0)
            
        if self.options.debug:
            if "AUTH_DOMAIN" not in os.environ:
                os.environ["AUTH_DOMAIN"] = "example.com"
            
        return options,args
    
    def help():
        self.parser.print_help()

    def load(self):
        """
        Load setting from application root
        """
        for p in [ "common/.google_appengine" , 
            "common/.google_appengine/lib"
            "common/google_appengine" , 
            "common/google_appengine/lib" , 
            "common/appenginepatch" ]:
            sys.path.append(self.basepath + "/" +  p)
        
        import yaml    
        
        stream = file(self.basepath + "/app.yaml") 
        self.app_id = yaml.load(stream)['application']
        
    def connect(self,debug=False,url=None,email = None, auth_func = None):
        """
       Connect to server
        """
        def _auth_func():
            if debug == False:
                if email != None:
                    return email,getpass.getpass('Password for %s:' % email)
                else:
                    return raw_input('Username:'), getpass.getpass('Password:')
            return "test@example.com",""

                
        if debug:
            self.host = url
        else:
            self.host = '%s.appspot.com' % self.app_id
            
        if auth_func == None:
            auth_func = _auth_func
        
        from google.appengine.ext.remote_api import remote_api_stub
        remote_api_stub.ConfigureRemoteDatastore(self.app_id, '/remote_api', auth_func, self.host)

        try:
            import main
        except ImportError:
            pass

        from django.conf import settings

    def download_model(self,model_class):
        entities = model_class.all().fetch(100)
        result = []

        while entities:
            for entry in entities:
                result.append(entry)

            entities = model_class.all().filter('__key__ >', entities[-1].key()).fetch(100)

        return result
    
    def upload_model(self,model_class,result):
        from google.appengine.ext import db
        from ragendja.dbutils import KeyListProperty
        from google.appengine.api.users import User
        
        def id_or_name(kind,value):
            ret = None
            try:
                id = int(value)
                ret = db.Key.from_path(kind , id)
            except ValueError:
                ret = db.Key.from_path(kind,value) 
            return ret
        
        def convert(entity):
            ret = {}
            for prop in model_class.properties().values():
                if not prop.name in entity:
                    continue

                if isinstance(prop,db.GeoPtProperty):
                    field = u",".join([str(v) for v in entity[prop.name]])
                    entity[prop.name] = field
                elif isinstance(prop,db.ReferenceProperty):
                    if prop.reference_class == db.Model:
                        entity[prop.name] = db.Key(encoded = entity[prop.name])
                    else:
                        try:
                            entity[prop.name] = id_or_name(prop.reference_class.kind(),entity[prop.name])
                        except TypeError:
                            del entity[prop.name]
                elif isinstance(prop,KeyListProperty):
                    items = []
                    for key in entity[prop.name]:
                        items.append(id_or_name(prop.reference_class.kind(),key))
                        
                    entity[prop.name] = items
                elif isinstance(prop,db.UserProperty):
                    entity[prop.name] = User(email = entity[prop.name])
                elif isinstance(prop,db.DateTimeProperty):
                    entity[prop.name] = datetime.datetime.fromtimestamp(entity[prop.name])
                
                if prop.name in entity and entity[prop.name] == None:
                    del entity[prop.name]
                    
            for key in entity:
                ret[str(key)] = entity[key]
                
            return ret
    
        save = []
        to_delete = []
        for entity in result:
                            
            id = None
            if "id" in entity:
                id = entity ["id"]
                del entity["id"]
                existing_entry = model_class.get(db.Key.from_path(model_class.kind(),id))
                if existing_entry:
                    to_delete.append(existing_entry)
                entity["key_name"] = "_" + str(id)
            
            #if not key:
                #print "No key assigned with record:"
                #print entity
                
            ret = convert(entity)
            object = model_class(**ret)
            
            save.append(object)
            
            if len(to_delete) > 100:
                db.delete(to_delete)
                to_delete = []
            if len(save) > 100:
                db.put(save)
                save = []
        
        db.delete(to_delete)    
        db.put(save)
        
    
        
