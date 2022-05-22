import json
import os

from coterieapp import app, bcrypt, db
from coterieapp.forms import LoginForm, RegistrationForm
from coterieapp.generate_profile import compareLikes, compareSubs, generate_liked_vids, generate_t5_categories, RelevantSubs, videorecs
from coterieapp.models import User
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user, login_required
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from uuid import uuid4

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

@app.route("/data")
def data():
    session["credentials"] = {
        "token": current_user.token,
        #"refresh_token": current_user.refresh_token,       # We do not need to refresh credentials
        "token_uri": current_user.token_uri,
        "client_id": current_user.client_id,
        "client_secret": current_user.client_secret,
        "scopes": current_user.scopes.split("<SEP>")
    }
    credentials = Credentials(**session["credentials"])
    youtube = build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )

    subscriptions = []
    next_page_token = None
    while 1:
        result = youtube.subscriptions().list(mine=True, part='snippet', maxResults=50, order='relevance', pageToken=next_page_token).execute()
        subscriptions.append(result['items'])
        next_page_token = result.get('nextPageToken')
        if next_page_token is None:
            break
    
    # print(subscriptions)

    jsonSubList = json.dumps(subscriptions) 
    jsonSubFile = open("{}.json".format(current_user.subs_filepath), "w")
    jsonSubFile.write(jsonSubList)
    jsonSubFile.close()

    print("Moving on to videos...")

    videos = []
    next_page_token = None
    while 1:
        result = youtube.videos().list(part='snippet', myRating='like', maxResults=50, pageToken=next_page_token).execute()
        videos.append(result['items'])
        next_page_token = result.get('nextPageToken')
        if next_page_token is None:
            break

    # print(videos)

    jsonVidList = json.dumps(videos)
    jsonVidFile = open("{}.json".format(current_user.vids_filepath), "w")
    jsonVidFile.write(jsonVidList)
    jsonVidFile.close()
    
    current_user.existing_data_profile = True

    return redirect(url_for("home"))

@app.route("/profile")
def profile():
    print(current_user.vids_filepath)
    # Returns a dict of top 5 categories
    top_5_categories = generate_t5_categories(current_user.vids_filepath)
    # Returns a list of most relevant subscriptions
    relevant_subs = RelevantSubs(current_user.subs_filepath)
    print(relevant_subs)
    return render_template("profile.html", t5=top_5_categories, 
        rsubs=relevant_subs)

@app.route("/compare")
def compare():
    user1subs = "speedob9bc650c10c54d5fb6302581387b3e52subs"
    user2subs = "sphenice36d32af674f4994b58acc26a7564154subs"
    top_common_subs = compareSubs(user1subs, user2subs)
    # print(top_common_subs)
    user1vids = "speedo3133755de2664b819a13198325c366edvids"
    user2vids = "sphenic8c82df195bd04699b5411acb300510aevids"
    top_liked_vids = compareLikes(user1vids, user2vids)
    video_recs = videorecs(user1vids, user2vids)
    return render_template("compare.html", common_subs=top_common_subs, common_likes=top_liked_vids, video_recs=video_recs)


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
            password=hashed_pw,
            subs_filepath=registration_form.username.data+uuid4().hex+"subs",
            vids_filepath=registration_form.username.data+uuid4().hex+"vids"
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

# Auxiliary function for joining filenames
def join_fn(folder, fn, ext):
    save_path = f"/{folder}"
    file_name = f"{fn}{ext}"
    complete_name = os.path.join(save_path, file_name)
    return complete_name
