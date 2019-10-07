import logging

from flask import Flask
import sentry_sdk


app = Flask(__name__)
app.config.from_object('config')

if app.config['SENTRY_URL']:
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(dsn=app.config['SENTRY_URL'], integrations=[FlaskIntegration()])


from app.views import JobRSSView
JobRSSView.register(app, route_base='/')
