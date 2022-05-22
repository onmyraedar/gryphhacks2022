from flask import Flask
from flask_session import Session
from os import getenv

app = Flask(__name__)
secret_key = getenv("SECRET_KEY")
app.config["SECRET_KEY"] = secret_key

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

from coterieapp import routes