# -*- coding: utf-8 -*-
from google.appengine.ext import db

def createEntity(object):
    """  Create an entity from model instance object which is 
    suitable for data import and export. 

    Opertions:
    - Convert all ReferenceProperty to the key_name/key
    """
    entity = {}

    for prop in object.properties().values():
        datastore_value = prop.get_value_for_datastore(object)
        if not datastore_value == []:
            entity[prop.name] = datastore_value
            
            if isinstance(prop,db.ReferenceProperty):
                if datastore_value:
                    entity[prop.name] = datastore_value.id_or_name()

    if object.key().has_id_or_name():
        if object.key().id() != None:
            entity['id'] = object.key().id()
        else:
            entity['key_name'] = object.key().name()
    else:
        entity['key'] = object.key()

    return entity

