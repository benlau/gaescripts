# -*- coding: utf-8 -*-
from google.appengine.ext import db

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

