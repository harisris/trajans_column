#kitchen/__init__.py
from flask import Flask

def create_app()
    from . import db, stove
    app = Flask(__name__)
    db.init_app(app)
    stove.init_app(app)
    return app
