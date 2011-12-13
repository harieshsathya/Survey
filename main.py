import cgi
import datetime
import os
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class UserInfo(db.Model):
  """Models the users info with id, name and email"""
  user = db.UserProperty(required=True,auto_current_user_add=True)

class Survey(db.Model):
  """Models a relationship between survey_id and author"""
  survey_id = db.IntegerProperty(required=True)
  survey_name = db.StringProperty(required=True)
  user = db.UserProperty(required=True,auto_current_user_add=True)
  date = db.DateTimeProperty(auto_now_add=True)

class SurveyDesc(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  survey_id = db.IntegerProperty(required=True)
  question = db.StringProperty(multiline=True)
  answers = db.ListProperty(str)

def Survey_Desc_Key(user_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Survey', user_name or 'Default_Survey')


class MainPage(webapp.RequestHandler):
  def get(self):
        User = users.get_current_user()
        if User:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Survey(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    pass
#    guestbook_name = self.request.get('guestbook_name')
#    greeting = Greeting(parent=guestbook_key(guestbook_name))

#    if users.get_current_user():
#      greeting.author = users.get_current_user()

#    greeting.content = self.request.get('content')
#    greeting.put()
#    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/my_survey', Survey)
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
