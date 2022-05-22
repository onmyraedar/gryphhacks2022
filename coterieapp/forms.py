from coterieapp.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username",
        validators=[DataRequired(), Length(min=5, max=40)])
    password = PasswordField("Password",
        validators=[DataRequired()])
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):
    username = StringField("Username",
        validators=[DataRequired(), Length(min=5, max=40)])
    password = PasswordField("Password",
        validators=[DataRequired()])
    submit = SubmitField("Sign Up")