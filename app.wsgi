activate_this = '/opt/directory/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import os

path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path)

from app import app as application