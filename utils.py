# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import datastore_types
import datetime
import time
import codecs
from StringIO import StringIO
id_prefix = "_"

def resolve_key(key_data,reference_class):
    """
    Resolve the key and create key instance
    """
    
    if isinstance(key_data, list): # If it is a path
        return db.Key.from_path(*key_data)
    elif isinstance(key_data, basestring):
        try:
            return db.Key(key_data) #Encoded data
        except datastore_types.datastore_errors.BadKeyError, e:
            if reference_class == db.Model:
                print "Warning! Invalid Reference."
                print entity
            else:
                return db.Key.from_path(reference_class.kind(),key_data)   

def encode_key(key,reference_class,field):
    """
    Encode a key for JSON output
    """
    if key.id():
        print "Warning! Field %s is referred to an entity with numeric ID(%d)" % (field , key.id())
        key_name = id_prefix + str(key.id())
    else:
        key_name = key.name()

    if reference_class != db.Model:
        return key_name
    else:
        if key.id() == None:
            return str(key)
        else:
            key = db.Key.from_path( key.kind() , key_name )
            return str(key)

def serialize(object):
    """ 
    Serialize a model instance to basic Python object

    Operations:
    - Convert all ReferenceProperty to the key_name/key
    """
    entity = {}
    
    for prop in object.properties().values():
        datastore_value = prop.get_value_for_datastore(object)
        if datastore_value == None:
            continue
        
        entity[prop.name] = datastore_value
        
        if isinstance(prop,db.ReferenceProperty):
            entity[prop.name] = encode_key(datastore_value,prop.reference_class,prop.name)
        elif isinstance(prop,db.GeoPtProperty):
            entity[prop.name] = (datastore_value.lat,datastore_value.lon)
        elif isinstance(prop,db.UserProperty):
            entity[prop.name] = datastore_value.email()
        elif isinstance(prop,db.DateTimeProperty):
            entity[prop.name] = time.mktime(datastore_value.timetuple())  

    if object.key().id() != None:
        entity['id'] = object.key().id()
    else:
        entity['key_name'] = object.key().name()


    return entity

def deserialize(model_class,entity):
    """
    Create a model instance from json
    """
    from google.appengine.ext import db
    from ragendja.dbutils import KeyListProperty
    from google.appengine.api.users import User    
    
    # GAE can not restore numeric ID entity
    if "id" in entity:
        id = entity ["id"]
        del entity["id"]
        entity["key_name"] = id_prefix + str(id)
        print "Warning. The entity with ID %d will be renamed to %s. Old record will be removed." % (id,entity["key_name"])
    
    for prop in model_class.properties().values():
        if not prop.name in entity:
            continue

        if isinstance(prop,db.GeoPtProperty):
            field = u",".join([str(v) for v in entity[prop.name]])
            entity[prop.name] = field
            
        elif isinstance(prop,db.ReferenceProperty):
            
            entity[prop.name] = resolve_key(entity[prop.name] , prop.reference_class)

        elif isinstance(prop,KeyListProperty):
            items = []
            for key in entity[prop.name]:
                items.append(resolve_key(key,prop.reference_class))
                
            entity[prop.name] = items
        elif isinstance(prop,db.UserProperty):
            entity[prop.name] = User(email = entity[prop.name])
        elif isinstance(prop,db.DateTimeProperty):
            entity[prop.name] = datetime.datetime.fromtimestamp(entity[prop.name])
        
        if prop.name in entity and entity[prop.name] == None:
            del entity[prop.name]
    
    ret = {}        
    for key in entity: #Convert unicode key to str key
        ret[str(key)] = entity[key]

    object = model_class(**ret)
        
    return object

def default(o):
    """
    ``default(obj)`` is a function that should return a serializable version
    of obj or raise TypeError for JSON generation
    """

    if isinstance(o,db.Key):
        return o.id_or_name()
    else:
        raise TypeError("%r is not JSON serializable" % (o,))   

class BackupFile:
    """
    Backup file
    """
    
    ver = 1
    
    def __init__(self,filename=None,model_class = None):
        self.filename = filename
        self.model_class = model_class
        self.model_kind = None
        
    def save(self,models):
        """
        Save the file
        
        @param models A list of model instance
        """
        from django.utils import simplejson
                
        entities = [serialize(m) for m in models]
        
        format = {
            "ver" : BackupFile.ver,
            "model_class" : self.model_class.kind(),
            "data" : entities
        }
        
        file = codecs.open(self.filename ,"wt","utf-8")
        
        text = StringIO()
	
        simplejson.dump(format,text,default=default,ensure_ascii=False,indent =1)
        
        file.write(text.getvalue())
        file.close()
        
    def load(self):
        """
        JSON instance from file
        """
        from django.utils import simplejson
        
        file = codecs.open(self.filename ,"rt","utf-8")
        data=""
        for line in file:
            data+=line
            
        format = simplejson.loads(data)
        
        if format["ver"] != BackupFile.ver:
            raise RuntimeError("Backup file version mismatched")
            
        self.model_kind = format["model_class"]
        result = format["data"]

        file.close()
        
        return result

    def get_model_class(self):
        return db._kind_map[self.model_kind]
        
        
        
    
    
