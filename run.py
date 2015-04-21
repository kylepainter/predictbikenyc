#!flask/bin/python
#import sys
#flaskfirst = "/sites/flaskfirst"
#if not flaskfirst in sys.path:
#    sys.path.insert(0, flaskfirst)


from app import app
app.run(host="0.0.0.0")
