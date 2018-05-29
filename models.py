from google.appengine.ext import ndb

class Message(ndb.Model):
    message = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default= False)
    username = ndb.StringProperty()