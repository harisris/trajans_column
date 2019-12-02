#kitchen/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchmey(app)



#def create_app()
#    from . import db, stove
#    app = Flask(__name__)
#    db = SQLAlchemy(app)
#    stove.init_app(app)
#    return app
