from coterieapp import app
from flask import jsonify, redirect, render_template, request, session, url_for
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
def home():
    return render_template("home.html")

@app.route("/authenticate")
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
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    print(credentials.token)
    print(credentials.refresh_token) 
    print(credentials.token_uri)
    print(credentials.client_id)   
    print(credentials.client_secret) 
    print(credentials.scopes) 

    # Clear the session once finished
    #if "credentials" in session:
    #    del session["credentials"]
    #if "state" in session:
    #    del session["state"]

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
    return jsonify(**subscriptions)