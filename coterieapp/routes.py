from coterieapp import app, bcrypt, db
from coterieapp.forms import LoginForm, RegistrationForm
from coterieapp.models import User
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user, login_required
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/youtube",
"https://www.googleapis.com/auth/youtube.force-ssl",
"https://www.googleapis.com/auth/youtube.readonly"
]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/authenticate")
@login_required
def authenticate():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback',
        _external=True
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    print(authorization_url)
    print(state)
    return redirect(authorization_url)

@app.route("/callback")
def oauth2callback():
    print("Callback function successfully accessed")
    state = session["state"]    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('oauth2callback',
        _external=True
    )
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)  
    credentials = flow.credentials

    # Saving user credentials in the database
    current_user.token = str(credentials.token)
    current_user.refresh_token = str(credentials.refresh_token)
    current_user.token_uri = str(credentials.token_uri)
    current_user.client_id = str(credentials.client_id)
    current_user.client_secret = str(credentials.client_secret)
    current_user.scopes = "<SEP>".join(credentials.scopes)

    # session["credentials"] = {
    #     "token": credentials.token,
    #     "refresh_token": credentials.refresh_token,
    #     "token_uri": credentials.token_uri,
    #     "client_id": credentials.client_id,
    #     "client_secret": credentials.client_secret,
    #     "scopes": credentials.scopes
    # }
    print(current_user.token)
    print(current_user.refresh_token) 
    print(current_user.token_uri)
    print(current_user.client_id)   
    print(current_user.client_secret) 
    print(current_user.scopes) 
    
    current_user.authorized = True

    # Clear the session once finished
    #if "credentials" in session:
    #    del session["credentials"]
    #if "state" in session:
    #    del session["state"]

    db.session.commit()

    flash("Your account has been successfully authenticated.", "secondary")
    return redirect(url_for("home"))

@app.route("/test")
def test():
    if "credentials" not in session:
        return redirect("authenticate")
    credentials = Credentials(**session["credentials"])
    youtube = build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )
    subscriptions = youtube.subscriptions().list(mine=True, part='snippet', maxResults=50, order='relevance').execute()
    print(subscriptions)
    print("Moving on to videos...")
    videos = youtube.videos().list(part='snippet', myRating='like', maxResults=50).execute()
    print(videos)
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    return jsonify(**videos)

# User management

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))   
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(registration_form.password.data).decode("utf-8")
        new_user = User(
            username=registration_form.username.data,
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()
        flash("You have successfully signed up for Coterie!", "secondary")
        return(redirect(url_for("login")))
    return render_template("register.html", form=registration_form)

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("We were unable to log you in. Please check your credentials.", "danger")
    return render_template("login.html", form=login_form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

# Auxiliary (non-route) functions