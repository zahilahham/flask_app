from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import pysqlite
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='./templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    

    from .views import main 
    app.register_blueprint(main)

    return app


create_app()