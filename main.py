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
  survey_name = db.StringProperty(required=True)
  user = db.UserProperty(required=True,auto_current_user_add=True)
  date = db.DateTimeProperty(auto_now_add=True)
  status = db.StringProperty(default='incomplete')

class SurveyDesc(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  survey_id = db.StringProperty(required=True)
  question = db.StringProperty(multiline=True)
  answers = db.ListProperty(str)

def Survey_Key(user_email=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('SurveyKey', user_email or 'default')


class MainPage(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      user_query = db.GqlQuery("SELECT * "
                               "FROM UserInfo "
                               "WHERE user = :1 ",
                               current_user)
      if not user_query:
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
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      survey_query = Survey.all().ancestor(Survey_Key(current_user.email())).order('-date')
      all_survey = survey_query.fetch(200)
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'surveys': all_survey,
    }

    path = os.path.join(os.path.dirname(__file__), 'display_survey.html')
    self.response.out.write(template.render(path, template_values))

  
class ViewMySurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      survey_desc_query = SurveyDesc.all().ancestor(Survey_Key(current_user.email()))
      all_survey_desc = survey_desc_query.fetch(200)
      current_survey = []
      for survey in all_survey_desc:
        if survey.survey_id == str(self.request.get('group1')):
          current_survey.append(survey)

      survey_query = Survey.all().ancestor(Survey_Key(current_user.email()))
      all_survey = survey_query.fetch(200)
      for survey in all_survey:
        date = str(survey.date)
        if(date == str(self.request.get('group1'))):
          current_survey_name = survey.survey_name

      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'surveys': current_survey,
      'survey_name': current_survey_name,
    }

    path = os.path.join(os.path.dirname(__file__), 'display_current_survey.html')
    self.response.out.write(template.render(path, template_values))


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
  def get(self): 
    current_user = users.get_current_user()
    if current_user:
      survey_query = Survey.all().order('-date')
      all_survey = survey_query.fetch(200)
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'surveys': all_survey,
    }

    path = os.path.join(os.path.dirname(__file__), 'display_survey.html')
    self.response.out.write(template.render(path, template_values))

class ViewAllSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      survey_desc_query = SurveyDesc.all()
      all_survey_desc = survey_desc_query.fetch(2000)
      current_survey = []
      for survey in all_survey_desc:
        if survey.survey_id == str(self.request.get('group1')):
          current_survey.append(survey)

      survey_query = Survey.all()
      all_survey = survey_query.fetch(2000)
      for survey in all_survey:
        date = str(survey.date)
        if(date == str(self.request.get('group1'))):
          current_survey_name = survey.survey_name

      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'surveys': current_survey,
      'survey_name': current_survey_name,
    }

    path = os.path.join(os.path.dirname(__file__), 'display_current_survey.html')
    self.response.out.write(template.render(path, template_values))


class Results(webapp.RequestHandler):
  def post(self):
    pass

class AddQuestion(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    
    if current_user:
      new_survey_desc = SurveyDesc(
          parent=Survey_Key(current_user.email()),
          survey_id=self.request.get('survey_id'),
          question=self.request.get('question')
          )
    
      option_list = []
      option1 = self.request.get('option1')
      option2 = self.request.get('option2')
      option3 = self.request.get('option3')
      option4 = self.request.get('option4')
      if option1:
        option_list.append(option1)
      if option2:
        option_list.append(option2)
      if option3:
        option_list.append(option3)
      if option4:
        option_list.append(option4)
      

      new_survey_desc.answers = option_list
      new_survey_desc.put()
    
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Logout'

    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktest': url_linktext,
      'survey_id': self.request.get('survey_id'),
    }
    
    
    if( self.request.get('submit') == "Finish"):
      all_survey = db.GqlQuery("SELECT * "
                               "FROM Survey "
                               "WHERE ANCESTOR IS :1 ",
                               Survey_Key(current_user.email()))
      
      for survey in all_survey:
        date = str(survey.date)
        if( date == self.request.get('survey_id') ):
          survey.status="complete"
          survey.put()
          break
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))
    else:
      path = os.path.join(os.path.dirname(__file__), 'add_question.html')
      self.response.out.write(template.render(path, template_values))
        

class AddSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    current_survey_name = str(self.request.get('survey_name'))
    if current_user:
      new_survey = Survey(
          parent=Survey_Key(current_user.email()),
          survey_name=current_survey_name
          )
      new_survey.put()
      survey_query = Survey.all().ancestor(Survey_Key(current_user.email())).order('-date')
      last_survey = survey_query.fetch(1)
      for survey in last_survey:
        last_survey_date = survey.date
        ss_name = survey.survey_name
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'survey_id': last_survey_date,
    }

    path = os.path.join(os.path.dirname(__file__), 'add_question.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/my_survey', MySurvey),
  ('/view_my_survey', ViewMySurvey),
  ('/all_survey', AllSurvey),
  ('/view_all_survey', ViewAllSurvey),
  ('/create', CreateSurvey),
  ('/add_survey', AddSurvey),
  ('/view_completed', Results),
  ('/add_question', AddQuestion)
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
