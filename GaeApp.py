# -*- coding: utf-8 -*-

import sys
import os
import getpass

class GaeApp:
    def __init__(self,path):
        self.basepath = os.path.abspath(path)
        self.app_id = None

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

                if isinstance(prop,db.GeoPtProperty):
                    if prop.name in entity:
                        field = u",".join([str(v) for v in entity[prop.name]])
                        entity[prop.name] = field
                elif isinstance(prop,db.ReferenceProperty):
                    if prop.name in entity:
                        try:
                            entity[prop.name] = id_or_name(prop.reference_class.kind(),entity[prop.name])
                        except TypeError:
                            del entity[prop.name]
                elif isinstance(prop,KeyListProperty):
                    items = []
                    for key in entity[prop.name]:
                        items.append(id_or_name(prop.reference_class.kind(),key))
                        
                    entity[prop.name] = items
                            
                if prop.name in entity and entity[prop.name] == None:
                    del entity[prop.name]
                    
            for key in entity:
                ret[str(key)] = entity[key]
                
            return ret
    
        save = []
        for entity in result:
            key_name = None
            if "key_name" in entity:
                key_name = entity["key_name"]
                del entity["key_name"]
                
            id = None
            if "id" in entity:
                id = entity ["id"]
                del entity["id"]
                
            ret = convert(entity)
            object = model_class(id = id , key_name = key_name,**ret)
            
            save.append(object)
            
        db.put(save)
        
    
        
