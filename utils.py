# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import datastore_types
import datetime

id_prefix = "_"

def resolve_key(key_data,reference_class):
    """
    Resolve the key and create key instance
    """
    
    if isinstance(key_data, list):
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

def createEntity(object):
    """  Create an entity from model instance object which is 
    suitable for data import and export. 

    Operations:
    - Convert all ReferenceProperty to the key_name/key
    """
    entity = {}
    
    for prop in object.properties().values():
        datastore_value = prop.get_value_for_datastore(object)
        if datastore_value == None:
            continue
        if not datastore_value == []:
            entity[prop.name] = datastore_value
            
            if isinstance(prop,db.ReferenceProperty):
                if datastore_value:
                    if prop.reference_class != db.Model:
                        
                        if datastore_value.id():
                            key_name = "_" + str(datastore_value.id())
                        else:
                            key_name = datastore_value.name()
                        entity[prop.name] = key_name
                    else:
                        entity[prop.name] = str(datastore_value)

    if object.key().has_id_or_name():
        if object.key().id() != None:
            entity['id'] = object.key().id()
        else:
            entity['key_name'] = object.key().name()
    else:
        entity['key'] = object.key()

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

