from google.appengine.ext import db

def drop(model):
    model_class = db._kind_map[model]
    
    entities = model_class.all().fetch(100)
    to_delete = []

    while entities:
        for entry in entities:
            to_delete.append(entry)

        entities = model_class.all().filter('__key__ >', entities[-1].key()).fetch(100)

    db.delete(to_delete)

def run(app,*models):
    __import__(app)
    for model in models:
        drop(model)
    
    
