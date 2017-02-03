"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import template, request, route, redirect, static_file

import logging

# this variable checks if the admin logged in
admin_flag = False


# This is the class that describes the record in the database
#
class Record(ndb.Model):
    username = ndb.StringProperty()
    ans1 = ndb.IntegerProperty()
    ans2 = ndb.IntegerProperty()
    ans3 = ndb.StringProperty()


# This is the function that adds a record to the database
def add_to_database(username, id, ans1, ans2, ans3):
    record = Record()
    record.ans1 = ans1
    record.ans2 = ans2
    record.ans3 = ans3
    record.username = username
    key = record.put()
    return key


def get_from_database(key):
    record = key.get()
    return record


# Create the Bottle WSGI application.
bottle = Bottle()


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# serve static files (js, css)
@bottle.route('/css/<filename:path>')
@bottle.route('/js/<filename:path>')
@bottle.route('/json/<filename:path>')
def static(filename):
    logging.info(filename)
    return static_file(filename, root='static')

# test post from jquery
@bottle.post('/posttest')
def posttest():
	logging.info("POSTTEST CALLED")
	logging.info(request.json)

# get questions
@bottle.get('/questions')
def getQuestions():
	return ""

# Define an handler for the root URL of our application.
@bottle.route('/login')
def login():
    if admin_flag == False:
        login = template('templates/login.html')
        return login
    else:
        redirect('/dashboard')


@bottle.post('/login')
def do_login():
    global admin_flag

    # This is the function that checks the login and password
    def check_login(username, password):
        if username == 'user' and password == 'admin':
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


@bottle.post('/survey')
def survey_post():
    pass


@bottle.route('/dashboard')
def dashboard():
    if admin_flag is True:
        dashboard = template('templates/dashboard.html')
        return dashboard
    else:
        redirect('/login')


# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'
