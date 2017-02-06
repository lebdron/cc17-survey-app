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


class QuestionsInRussian(ndb.Model):
    value_json = ndb.JsonProperty()


class QuestionsInEnglish(ndb.Model):
    value_json = ndb.JsonProperty()


def add_answer_to_database(survey_json):
    answers = Answers()
    answers.value_json = survey_json
    key = answers.put()
    return key


def add_questions_in_russian_to_database(question_json):
    ndb.delete_multi(QuestionsInRussian.query().fetch(keys_only=True))
    questions_in_russian = QuestionsInRussian()
    questions_in_russian.value_json = question_json
    key = questions_in_russian.put()
    return key


def add_questions_in_english_to_database(question_json):
    ndb.delete_multi(QuestionsInEnglish.query().fetch(keys_only=True))
    questions_in_english = QuestionsInEnglish()
    questions_in_english.value_json = question_json
    key = questions_in_english.put()
    return key


def add_admin_to_database(admin_json):
    ndb.delete_multi(Admin.query().fetch(keys_only=True))
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
    return result


@bottle.post('/questions_in_russian')
def add_questions_in_russian():
    add_questions_in_russian_to_database(request.json)


@bottle.post('/questions_in_english')
def add_questions_in_english():
    add_questions_in_english_to_database(request.json)


@bottle.get('/questions_in_russian')
def get_questions_in_russian():
    questions_in_russian = QuestionsInRussian.query().fetch()
    return questions_in_russian[-1].value_json


@bottle.get('/questions_in_english')
def get_questions_in_english():
    questions_in_english = QuestionsInEnglish.query().fetch()
    return questions_in_english[-1].value_json


@bottle.post('/admin')
def add_admin():
    add_admin_to_database(request.json)


@bottle.get('/set_parameters')
def set_parameters():
    return template('templates/set_parameters.html')


# Define an handler for the root URL of our application.
@bottle.route('/login')
def login():
    if admin_flag == False:
        login = template('templates/login.html')
        return login
    else:
        redirect('/dashboard')


def compute_average_scores():
    answers = Answers.query().fetch()
    questions = QuestionsInEnglish.query().fetch()
    rating_questions = []
    for question in questions[0].value_json['pages'][0]['questions']:
        if question['type'] == 'rating':
            rating_questions.append(question['name'])
    average_values = []
    for rq in rating_questions:
        average = 0.0
        count = 0
        for answer in answers:
            average += int(answer.value_json[rq])
            count += 1
        average = average / count
        average_values.append((rq, average))
    return average_values


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
        scores = compute_average_scores()
        logging.error(scores)
        dashboard = template('templates/dashboard.html', scores=scores)
        return dashboard
    else:
        redirect('/login')


@bottle.post('/logout')
def logout():
    global admin_flag
    if not (logout is None):
        admin_flag = False


def redirect_back():
    if admin_flag == False:
        redirect('/login')


# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'



