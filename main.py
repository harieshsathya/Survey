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

def Survey_Key(user_email=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('SurveyKey', user_email or 'default')


class MainPage(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      current_user_info = UserInfo()
      current_user_info.user = current_user;
      current_user_info.put()
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


class MySurvey(webapp.RequestHandler):
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


class CreateSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'create_survey.html')
    self.response.out.write(template.render(path, template_values))

class AllSurvey(webapp.RequestHandler):
  def post(self):
    pass

class Results(webapp.RequestHandler):
  def post(self):
    pass

class AddSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    next_survey_id = 1
    if current_user:
      survey_query = Survey.all().ancestor(Survey_Key(current_user.email())).order('-date')
      last_survey = survey_query.fetch(1)
      for survey in last_survey:
        next_survey_id = survey.survey_id + 1
      new_survey = Survey(
          parent=Survey_Key(current_user.email()),
          survey_id=next_survey_id,
          survey_name=self.request.get('survey_name')
          )
      new_survey.put()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'survey_id': next_survey_id,
    }

    path = os.path.join(os.path.dirname(__file__), 'add_question.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/my_survey', MySurvey),
  ('/all_survey', AllSurvey),
  ('/create', CreateSurvey),
  ('/add_survey', AddSurvey),
  ('/view_completed', Results)
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
