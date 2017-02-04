"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import template, request, route, redirect, static_file
from google.appengine.ext import ndb
import json

import logging

admin_flag = False


class Admin(ndb.Model):
    value_json = ndb.JsonProperty()


class Answers(ndb.Model):
    value_json = ndb.JsonProperty()


class Questions(ndb.Model):
    value_json = ndb.JsonProperty()


def add_answer_to_database(survey_json):
    answers = Answers()
    answers.value_json = survey_json
    key = answers.put()
    return key


def add_questions_to_database(question_json):
    questions = Questions()
    questions.value_json = question_json
    key = questions.put()
    return key


def add_admin_to_database(admin_json):
    admin = Admin()
    admin.value_json = admin_json
    key = admin.put()
    return key


def get_from_database(key):
    value = key.get()
    return value


# Create the Bottle WSGI application.
bottle = Bottle()


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@bottle.route('/css/<filename:path>')
@bottle.route('/js/<filename:path>')
@bottle.route('/json/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


# test post from jquery
@bottle.post('/survey_add_answers')
def add_survey_answers():
    add_answer_to_database(request.json)


# get all submissions
@bottle.route('/submissions')
def get_submissions():
    submissions = Answers.query().fetch(keys_only=True)
    return template('templates/submissions.html', submissions=submissions)


@bottle.get('/<id>')
def get_submission(id):
    answers = ndb.Key('Answers', int(id)).get()
    return answers.value_json


@bottle.get('/answers')
def get_submission():
    answers = Answers.query().fetch()
    result = {}
    for answer in answers:
        result[answer.key.id()] = answer.value_json
    logging.error(result)
    return result


@bottle.post('/questions')
def add_questions():
    add_questions_to_database(request.json)


@bottle.get('/questions')
def get_questions():
    questions = Questions.query().fetch()
    return questions[-1].value_json


@bottle.post('/admin')
def add_admin():
    add_admin_to_database(request.json)


@bottle.get('/set_parameters')
def set_parameters():
    redirect_back()
    return template('templates/set_parameters.html')


# Define an handler for the root URL of our application.
@bottle.route('/login')
def login():
    if admin_flag == False:
        login = template('templates/login.html')
        return login
    else:
        redirect('/dashboard')


@bottle.post('/login')
def login():
    global admin_flag

    def check_login(username, password):
        admin = Admin.query().fetch()[0]
        if username == admin.value_json['username'] and password == admin.value_json['password']:
            return True
        else:
            return False

    username = request.forms.get('login')
    password = request.forms.get('password')

    if check_login(username, password):
        admin_flag = True
        redirect('/dashboard')
    else:
        return template('<p>Login Failed</p>')


@bottle.route('/')
@bottle.route('/survey')
def survey():
    if admin_flag == False:
        survey = template('templates/index.html')
        return survey
    else:
        redirect('/dashboard')


@bottle.route('/dashboard')
def dashboard():
    if admin_flag is True:
        dashboard = template('templates/dashboard.html')
        return dashboard
    else:
        redirect('/login')


@bottle.post('/dashboard')
def logout():
    global admin_flag
    logout = request.forms.get('logout_button')
    if not (logout is None):
        admin_flag = False
        redirect('/')


def redirect_back():
    if admin_flag == False:
        redirect('/login')


# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'
