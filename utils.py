# -*- coding: utf-8 -*-
from google.appengine.ext import db
import datetime

def createEntity(object):
    """  Create an entity from model instance object which is 
    suitable for data import and export. 

    Operations:
    - Convert all ReferenceProperty to the key_name/key
    """
    entity = {}

    for prop in object.properties().values():
        datastore_value = prop.get_value_for_datastore(object)
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

def id_or_name(kind,value):
    ret = None
    try:
        id = int(value)
        ret = db.Key.from_path(kind , id)
    except ValueError:
        ret = db.Key.from_path(kind,value) 
    return ret

def fromJSON(model_class,entity):
    """
    Create a model instance from json
    """
    from google.appengine.ext import db
    from ragendja.dbutils import KeyListProperty
    from google.appengine.api.users import User    
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
            
    for key in entity: #Convert unicode key to str key
        ret[str(key)] = entity[key]
        
    object = model_class(**ret)
        
    return object

