import requests.packages.urllib3
from flask import Flask

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)
app.config.from_object('config')

from app.views import JobRSSView
JobRSSView.register(app, route_base='/')