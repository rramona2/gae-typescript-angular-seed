#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from models import Question

from settings import WEB_CLIENT_ID

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@endpoints.api( name='higherme',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class HigherMeApi(remote.Service):
    """HigherMeApi API v0.1"""


# - - - Question objects - - - - - - - - - - - - - - - - - -

    def _newQuestion(self, request):
        """Create a new Question and return a QuestionForm"""
        if request:
            question = Question.Question(
                questionText = request.questionText,
                questionnaire = str(request.questionnaire),
                order = request.order,
                questionType = str(request.questionType)
            )
            question.put()
            return request


    def _nextQuestion(self, request):
        """Get the next Question in a Questionnaire and return a QuestionForm"""
        next_question = Question.Question.query(Question.Question.order > request.order, Question.Question.questionnaire == str(request.questionnaire)).order(Question.Question.order).fetch(1)[0]
        qf = Question.QuestionForm()
        for field in qf.all_fields():
            if hasattr(next_question, field.name):
                if field.name == 'questionType':
                    setattr(qf, field.name, getattr(Question.QuestionType, getattr(next_question, field.name)))
                elif field.name == 'questionnaire':
                    setattr(qf, field.name, getattr(Question.Questionnaire, getattr(next_question, field.name)))
                else:
                    setattr(qf, field.name, getattr(next_question, field.name))
        return qf


    @endpoints.method(Question.QuestionForm, Question.QuestionForm,
            path='question', http_method='POST', name='question')
    def question(self, request):
        """Endpoint to create a new Question"""
        return self._newQuestion(request)

    @endpoints.method(Question.NextQuestionForm, Question.QuestionForm,
                      path='question/next', http_method='GET', name='nextQuestion')
    def nextQuestion(self, request):
        """Endpoint to return the next Question in a Questionnaire"""
        return self._nextQuestion(request)




# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    # def _copyProfileToForm(self, prof):
    #     """Copy relevant fields from Profile to ProfileForm."""
    #     # copy relevant fields from Profile to ProfileForm
    #     pf = ProfileForm()
    #     for field in pf.all_fields():
    #         if hasattr(prof, field.name):
    #             # convert t-shirt string to Enum; just copy others
    #             if field.name == 'teeShirtSize':
    #                 setattr(pf, field.name, getattr(TeeShirtSize, getattr(prof, field.name)))
    #             else:
    #                 setattr(pf, field.name, getattr(prof, field.name))
    #     pf.check_initialized()
    #     return pf
    #
    #
    # def _getProfileFromUser(self):
    #     """Return user Profile from datastore, creating new one if non-existent."""
    #     ## TODO 2
    #     ## step 1: make sure user is authed
    #     ## uncomment the following lines:
    #     # user = endpoints.get_current_user()
    #     # if not user:
    #     #     raise endpoints.UnauthorizedException('Authorization required')
    #     profile = None
    #     ## step 2: create a new Profile from logged in user data
    #     ## you can use user.nickname() to get displayName
    #     ## and user.email() to get mainEmail
    #     if not profile:
    #         profile = Profile(
    #             userId = None,
    #             key = None,
    #             displayName = "Test",
    #             mainEmail= None,
    #             teeShirtSize = str(TeeShirtSize.NOT_SPECIFIED),
    #         )
    #
    #     return profile      # return Profile
    #
    #
    # def _doProfile(self, save_request=None):
    #     """Get user Profile and return to user, possibly updating it first."""
    #     # get user Profile
    #     prof = self._getProfileFromUser()
    #
    #     # if saveProfile(), process user-modifyable fields
    #     if save_request:
    #         for field in ('displayName', 'teeShirtSize'):
    #             if hasattr(save_request, field):
    #                 val = getattr(save_request, field)
    #                 if val:
    #                     setattr(prof, field, str(val))
    #
    #     # return ProfileForm
    #     return self._copyProfileToForm(prof)
    #
    #
    # @endpoints.method(message_types.VoidMessage, ProfileForm,
    #         path='profile', http_method='GET', name='getProfile')
    # def getProfile(self, request):
    #     """Return user profile."""
    #     return self._doProfile()
    #
    # # TODO 1
    # # 1. change request class
    # # 2. pass request to _doProfile function
    # @endpoints.method(ProfileMiniForm, ProfileForm,
    #         path='profile', http_method='POST', name='saveProfile')
    # def saveProfile(self, request):
    #     """Update & return user profile."""
    #     return self._doProfile(request)


# registers API
api = endpoints.api_server([HigherMeApi])

#
# template_directory = os.path.join(os.path.dirname(__file__), 'templates')
# jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_directory),
#                                        autoescape = True)
#
# class Helper(webapp2.RequestHandler):
#     def write(self, *a, **kw):
#         self.response.out.write(*a, **kw)
#
#     def render_str(self, template, **params):
#         t = jinja_environment.get_template(template)
#         return t.render(params)
#
#     def render(self, template, **kw):
#         self.write(self.render_str(template, **kw))
#
# class MainHandler(Helper):
#     def get(self):
#         self.render('index.html')
#
# app = webapp2.WSGIApplication([
#     ('/', MainHandler)
# ], debug=True)
