import logging

import requests.packages.urllib3
from flask import Flask
from raven.contrib.flask import Sentry

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)
app.config.from_object('config')

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

from app.views import JobRSSView
JobRSSView.register(app, route_base='/')