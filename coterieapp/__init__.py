from flask import Flask
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)
secret_key = getenv("SECRET_KEY")
app.config["SECRET_KEY"] = secret_key

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

login_manager = LoginManager(app)

# Redirects the user to the login page if they are attempting to access a restricted page without logging in
login_manager.login_view = "login"
login_manager.login_message_category = "secondary"

from coterieapp import routes