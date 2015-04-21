#!flask/bin/python
#import sys
#flaskfirst = "/sites/flaskfirst"
#if not flaskfirst in sys.path:
#    sys.path.insert(0, flaskfirst)
import os

from app import app
#
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
