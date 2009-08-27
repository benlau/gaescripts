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
            host = url
        else:
            host = '%s.appspot.com' % self.app_id
            
        if auth_func == None:
            auth_func = _auth_func
        
        from google.appengine.ext.remote_api import remote_api_stub
        remote_api_stub.ConfigureRemoteDatastore(self.app_id, '/remote_api', auth_func, host)
        
        print "App Engine remote utils for %s at %s" % (self.app_id,host)

        try:
            import main
        except ImportError:
            pass

        from django.conf import settings
