#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Message
from google.appengine.api import users
from google.appengine.api import urlfetch
import json


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        
        user = users.get_current_user()
        login_url = users.create_login_url('/chat')
        logout_url = users.create_logout_url('/')
        is_admin = users.is_current_user_admin()

        params["login_url"]= login_url
        params["logout_url"] = logout_url
        params["user"] = user
        params["admin"] = is_admin

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:

            return self.redirect_to("chat")
        else:    

            return self.render_template("main.html")

    
class ChatHandler(BaseHandler):

    def get(self):

        messages = Message.query(Message.deleted == False).order(Message.created)
        params = {"messages": messages}

        return self.render_template("chat.html", params=params)

    def post(self):

        user = users.get_current_user()

        message = self.request.get("message")
        new_message = Message(message = message, username= user.nickname())
        new_message.put()
            
        return self.redirect_to("chat")

class DeleteMessageHandler(BaseHandler):

    def get(self, message_id):
        message = Message.get_by_id(int(message_id))

        params = {"message": message}

        return self.render_template("delete-message.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))

        message.deleted = True  
        message.put()

        return self.redirect_to("chat")

class WeatherHandler(BaseHandler):
   def get(self):
       url = "http://api.openweathermap.org/data/2.5/weather?q=Maribor&units=metric&appid=2b9448f3b7960c3e992c3d62064c5f19"
       result= urlfetch.fetch(url)
       json_data = json.loads(result.content)

       params = {"weather": json_data}
        
       return self.render_template("weather.html", params = params)

   def post(self):

        city = self.request.get("city")
        url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&units=metric&appid=2b9448f3b7960c3e992c3d62064c5f19"
        result = urlfetch.fetch(url)
        json_data = json.loads(result.content)

        params = {"weather": json_data}
            
        return self.render_template("weather.html", params = params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/chat', ChatHandler, name="chat"),
    webapp2.Route('/chat/<message_id:\d+>/delete', DeleteMessageHandler),
    webapp2.Route('/weather', WeatherHandler),
], debug=True)
