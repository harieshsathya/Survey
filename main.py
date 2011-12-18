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
  qno = db.IntegerProperty()
  question = db.StringProperty(multiline=True)
  answers = db.ListProperty(str)

class Votes(db.Model):
  survey_id = db.StringProperty()
  qno = db.IntegerProperty()
  option1 = db.IntegerProperty(default=0)
  option2 = db.IntegerProperty(default=0)
  option3 = db.IntegerProperty(default=0)
  option4 = db.IntegerProperty(default=0)

class UserVoteRecord(db.Model):
  survey_id = db.StringProperty()
  users = db.ListProperty(users.User)

def Survey_Key(user_email=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('SurveyKey', user_email or 'default')

def question_key(survey_id=None):
  return db.Key.from_path('QuestionKey', survey_id or 'default')


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
      survey_desc_query = SurveyDesc.all().ancestor(question_key(self.request.get('group1')))
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
          status = survey.status

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
      'survey_id': self.request.get('group1'),
      'status': status,
    }

    path = os.path.join(os.path.dirname(__file__), 'display_current_survey.html')
    self.response.out.write(template.render(path, template_values))


class EditSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    current_survey_id = self.request.get('survey_id')
    if current_user:
      survey_query = Survey.all().ancestor(Survey_Key(current_user.email())).order('-date')
      survey_list = survey_query.fetch(2000)
      for survey in survey_list:
        if str(survey.date) == current_survey_id:
          current_survey_name=survey.survey_name
          survey.status="deleted"
          survey.put()
          break

      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'delete_survey_name': current_survey_name,
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class VoteSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      survey_query = Survey.all().order('-date')
      all_survey = survey_query.fetch(2000)
      current_survey = []
      finished_survey = []

      for survey in all_survey:
        flag=True
        user_query = UserVoteRecord.all().ancestor(question_key(str(survey.date)))
        reg_user = user_query.fetch(1)
        if reg_user:
          flag=True
          for item in reg_user:
            for user_det in item.users:
              if user_det.email() == current_user.email():
                flag=False
                break
          if flag:
            current_survey.append(survey)
          else:
            finished_survey.append(survey)
        else:
          current_survey.append(survey)

      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'surveys': current_survey,
      'finished_surveys': finished_survey,
    }

    path = os.path.join(os.path.dirname(__file__), 'vote_survey.html')
    self.response.out.write(template.render(path, template_values))


class VoteMySurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      survey_desc_query = SurveyDesc.all().ancestor(question_key(self.request.get('group1')))
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
      'survey_id': self.request.get('group1'),
    }

    path = os.path.join(os.path.dirname(__file__), 'vote_current_survey.html')
    self.response.out.write(template.render(path, template_values))

class RegisterVote(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    current_survey_id = self.request.get('survey_id')
    if current_user:
      survey_desc_query = SurveyDesc.all().ancestor(question_key(current_survey_id))
      all_survey_desc = survey_desc_query.fetch(2000)
      current_survey = []
      for survey in all_survey_desc:
        if survey.survey_id == current_survey_id:
          current_survey.append(survey)

      for survey in current_survey:
        number=str(survey.qno)
        answer=self.request.get(number)
        i=1
        
        for ans in survey.answers:
          if ans == answer:
            break
          else:
            i = i + 1
        
        existing_vote_query = Votes.all().ancestor(question_key(current_survey_id))
        existing_vote = existing_vote_query.fetch(2000)

        flag=True
        for vote in existing_vote:
          if vote.qno == survey.qno:
            flag = False
            if i==1:
              vote.option1 = vote.option1 + 1
            if i==2:
              vote.option2 = vote.option2 + 1
            if i==3:
              vote.option3 = vote.option3 + 1
            if i==4:
              vote.option4 = vote.option4 + 1
            vote.put()

        if flag:
          new_vote = Votes(parent=question_key(current_survey_id))
          new_vote.qno=survey.qno
          new_vote.survey_id=current_survey_id
          if i==1:
            cv = new_vote.option1
            new_vote.option1 = cv + 1
          if i==2:
            cv = new_vote.option2
            new_vote.option2 = cv + 1
          if i==3:
            cv = new_vote.option3
            new_vote.option3 = cv + 1
          if i==4:
            cv = new_vote.option4
            new_vote.option4 = cv + 1
          new_vote.put()
        
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    reg_user_query = UserVoteRecord.all().ancestor(question_key(current_survey_id))
    reg_user = reg_user_query.fetch(2000)
    
    if reg_user:
      for id in reg_user:
        if id.survey_id == current_survey_id:
          id.users.append(current_user)
          id.put()
          break
    else:
      new_reg = UserVoteRecord(parent=question_key(current_survey_id))
      new_reg.survey_id = current_survey_id
      new_reg.users.append(current_user)
      new_reg.put()

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'survey_name': "name",
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
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

    path = os.path.join(os.path.dirname(__file__), 'display_all_survey.html')
    self.response.out.write(template.render(path, template_values))

class ViewAllSurvey(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
      survey_desc_query = SurveyDesc.all().ancestor(question_key(self.request.get('group1')))
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

    path = os.path.join(os.path.dirname(__file__), 'view_results_survey.html')
    self.response.out.write(template.render(path, template_values))

class ShowResults(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    current_survey_id = self.request.get('group1')
    if current_user:
      survey_desc_query = SurveyDesc.all().ancestor(question_key(current_survey_id))
      all_survey_desc = survey_desc_query.fetch(2000)
      current_survey = []
      for survey in all_survey_desc:
        if survey.survey_id == current_survey_id:
          current_survey.append(survey)

      result_query = Votes.all().ancestor(question_key(current_survey_id))
      results = result_query.fetch(2000)
      current_results = []
      for result in results:
        if result.survey_id == current_survey_id:
          current_results.append(result)

      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'surveys': current_survey,
      'results': current_results,
    }

    path = os.path.join(os.path.dirname(__file__), 'show_results.html')
    self.response.out.write(template.render(path, template_values))

class AddQuestion(webapp.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    
    if current_user:
      new_survey_desc = SurveyDesc(
          parent=question_key(self.request.get('survey_id')),
          survey_id=self.request.get('survey_id'),
          question=self.request.get('question')
          )

      current_qno=1
      get_survey_desc = SurveyDesc.all().ancestor(question_key(self.request.get('survey_id'))).order('-survey_id').order('-qno')
      get_survey = get_survey_desc.fetch(1)
      for survey in get_survey:
        if survey.survey_id == self.request.get('survey_id'):
          current_qno=survey.qno+1
    
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
      new_survey_desc.qno = current_qno
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
      survey_check_q = db.GqlQuery("SELECT  * FROM Survey WHERE survey_name = :1", current_survey_name)
      survey_check = survey_check_q.fetch(1)
      if survey_check:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
          'url': url,
          'url_linktext': url_linktext,
          'error': "Survey Name Already Exists",
        }
      
        path = os.path.join(os.path.dirname(__file__), 'error.html')
        self.response.out.write(template.render(path, template_values))
        return
      
      else:
        new_survey = Survey(
            parent=Survey_Key(current_user.email()),
            survey_name=current_survey_name
            )
        new_survey.put()
        survey_query = Survey.all().ancestor(Survey_Key(current_user.email())).order('-date')
        last_survey = survey_query.fetch(1)
        for survey in last_survey:
          last_survey_date = survey.date
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
  ('/show_result', ShowResults),
  ('/add_question', AddQuestion),
  ('/vote', VoteSurvey),
  ('/vote_my_survey', VoteMySurvey),
  ('/vote_current', RegisterVote),
  ('/edit_survey', EditSurvey)
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
