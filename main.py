"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle
from bottle import template

# Create the Bottle WSGI application.
bottle = Bottle()
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


# Define an handler for the root URL of our application.
@bottle.route('/')
def login():
    login = template('templates/login.html')
    return login

@bottle.route('/survey')
def survey():
    survey = template('templates/survey.html')
    return survey

@bottle.route('/dashboard')
def dashboard():
    dashboard = template('templates/dashboard.html')
    return dashboard

# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'

