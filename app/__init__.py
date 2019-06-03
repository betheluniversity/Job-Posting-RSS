import logging

from flask import Flask
from raven.contrib.flask import Sentry


app = Flask(__name__)
app.config.from_object('config')

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.ERROR)

from app.views import JobRSSView
JobRSSView.register(app, route_base='/')
